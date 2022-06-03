import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    num_pages = len(corpus.items())
    num_links = len(corpus[page])
    probabilities = {}

    # If the page has not outgoing links
    if num_links == 0:
        each_prob = 1/num_pages
        for key in corpus.keys():
            probabilities[key] = each_prob
        return probabilities

    # Distribute the probabilities from using an on-page link
    for link in corpus[page]:
        probabilities[link] = damping_factor/num_links

    # Add the probability that each page has due to the damping factor
    each_prob = (1 - damping_factor) / num_pages
    for link, probability in probabilities.items():
        probability += each_prob

    return probabilities


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    samples = []
    pages = list(corpus.keys())
    num_pages = len(pages)
    probabilities = {}

    # Get initial random sample
    first_sample = pages[random.randint(0, num_pages-1)]
    samples.append(first_sample)

    # For the rest (n-1) samples, use the transition model that comes from the previous sample
    previous_sample = first_sample
    for i in range(n-1):
        t_model = transition_model(corpus, previous_sample, damping_factor)

        # Choose a page to visit based on the corresponding probability distribution
        new_sample = random.choices(list(t_model.keys()), weights=list(t_model.values()), k=1)[0]
        samples.append(new_sample)
        previous_sample = new_sample

    # Find the probability of each page to be a sample
    for page in pages:
        probabilities[page] = samples.count(page) / n

    return probabilities


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    def max_change_in_probabilities(first, second):
        max_change = 0
        for page, prob in first.items():
            max_change = max(abs(prob - second[page]), max_change)

        return max_change

    pages = corpus.keys()
    num_pages = len(pages)
    probabilities = {}

    # Give probabilities an initial random assignment
    for page in pages:
        probabilities[page] = 1/num_pages

    change_in_probability = 1  # Initialize this at a value > 0.001
    # Update probabilities using the PageRank recursive formula
    while change_in_probability > 0.001:
        new_probabilities = probabilities.copy()

        # Iterate over pages in corpus to assign new probabilities
        for page, prob in probabilities.items():
            # Start the new probability with the initial random chance due to damping
            new_prob = (1 - damping_factor)/num_pages

            # Add to the probability by computing the pagerank of the page based on the links from other pages
            for other_page in pages:
                rank_prob = 0

                # Check to not sum over the page itself or pages that do not link to the page
                if other_page != page and page in corpus[other_page]:
                    # Add the PageRank(i) divided by NumLinks(i) and scaled by the damping factor
                    rank_prob += damping_factor*probabilities[other_page]/len(corpus[other_page])

                new_prob += rank_prob
            new_probabilities[page] = new_prob

        # Now that we have the new probabilities, we can find the max change to know whether or not to continue
        change_in_probability = max_change_in_probabilities(probabilities, new_probabilities)
        probabilities = new_probabilities.copy()

    return probabilities


if __name__ == "__main__":
    main()
