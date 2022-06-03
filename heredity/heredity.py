import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    # Initialize probability to 1, which will decrease as we multiply out the actual probabilities
    probability = 1
    individual_prob = []

    # Define probabilities of passing good or bad genes

    # 50% * 99% chance of passing good gene un-mutated
    # and a 50% * 1% chance of passing a bad gene that has mutated to good
    prob_1_to_good = (0.5 * PROBS["mutation"] + 0.5 * (1 - PROBS["mutation"]))
    prob_1_to_bad = 1 - prob_1_to_good

    # 1% chance of passing a mutated to good gene
    prob_2_to_good = PROBS["mutation"]
    prob_2_to_bad = 1 - prob_2_to_good

    # 99$ chance of passing a good gene that does not mutate
    prob_0_to_good = 1 - PROBS["mutation"]
    prob_0_to_bad = 1 - prob_0_to_good

    # To help out, we will add people to zero_genes if they are not in one_gene or two_genes
    zero_genes = set()
    for person in people.keys():
        if person not in one_gene and person not in two_genes:
            zero_genes.add(person)

    def parent_condition(mother, father):
        """
        Determine the combination of parents' genes
        returns
        "2-2" if both parents have 2 genes
        "1-1" if both parents have 1 gene
        "0-0" if both parents have 0 genes
        "1-2" if one parent has 1 gene, and the other has 2
        "0-2" if one parent has 0 genes, and the other has 2
        "0-1" if one parent has 0 genes, and the other has 1
        """
        # Both parents have 2 genes
        if mother in two_genes and father in two_genes:
            return "2-2"
        # Both parents have 0 genes
        elif mother in zero_genes and father in zero_genes:
            return "0-0"
        # Both parents have 1 gene
        elif mother in one_gene and father in one_gene:
            return "1-1"
        elif (mother in one_gene and father in two_genes) or (mother in two_genes and father in one_gene):
            return "1-2"
        elif (mother in one_gene and father in zero_genes) or (mother in zero_genes and father in one_gene):
            return "0-1"
        elif (mother in zero_genes and father in two_genes) or (mother in two_genes and father in zero_genes):
            return "0-2"
        else:
            print("There is another parent condition that is not accounted for")

    # Now we can check probabilities of each event happening
    for person in people.keys():

        '''We will first compute gene presence probability'''
        # Does the person have 1 gene
        if person in one_gene:

            # Does the person have parents
            if people[person]["mother"] is not None and people[person]["father"] is not None:
                # Probability of getting good from father and bad from mother
                # or bad from father and good from mother
                condition = parent_condition(people[person]["mother"], people[person]["father"])
                if condition == "2-2":
                    individual_prob.append(2 * (prob_2_to_good * prob_2_to_bad))
                elif condition == "1-1":
                    individual_prob.append(2 * (prob_1_to_good * prob_1_to_bad))
                elif condition == "0-0":
                    individual_prob.append(2 * (prob_0_to_good * prob_0_to_bad))
                elif condition == "1-2":
                    individual_prob.append((prob_1_to_good * prob_2_to_bad) + (prob_1_to_bad * prob_2_to_good))
                elif condition == "0-2":
                    individual_prob.append((prob_0_to_good * prob_2_to_bad) + (prob_0_to_bad * prob_2_to_good))
                elif condition == "0-1":
                    individual_prob.append((prob_0_to_good * prob_1_to_bad) + (prob_0_to_bad * prob_1_to_good))

            else:  # This person does not have parents' data
                individual_prob.append(PROBS["gene"][1])

        elif person in two_genes:  # Does the person have 2 genes
            # Does the person have parents
            if people[person]["mother"] is not None and people[person]["father"] is not None:
                # Probability of getting bad from father and bad from mother
                condition = parent_condition(people[person]["mother"], people[person]["father"])
                if condition == "2-2":
                    individual_prob.append(prob_2_to_bad ** 2)
                elif condition == "1-1":
                    individual_prob.append(prob_1_to_bad ** 2)
                elif condition == "0-0":
                    individual_prob.append(prob_0_to_bad ** 2)
                elif condition == "1-2":
                    individual_prob.append(prob_1_to_bad * prob_2_to_bad)
                elif condition == "0-2":
                    individual_prob.append(prob_0_to_bad * prob_2_to_bad)
                elif condition == "0-1":
                    individual_prob.append(prob_0_to_bad * prob_1_to_bad)

            else:  # This person does not have parents' data
                individual_prob.append(PROBS["gene"][2])

        else:  # Does the person have 0 genes?

            # Does the person have parents
            if people[person]["mother"] is not None and people[person]["father"] is not None:
                # Probability of getting good from father and good from mother
                condition = parent_condition(people[person]["mother"], people[person]["father"])
                if condition == "2-2":
                    individual_prob.append(prob_2_to_good ** 2)
                elif condition == "1-1":
                    individual_prob.append(prob_1_to_good**2)
                elif condition == "0-0":
                    individual_prob.append(prob_0_to_good**2)
                elif condition == "1-2":
                    individual_prob.append(prob_1_to_good * prob_2_to_good)
                elif condition == "0-2":
                    individual_prob.append(prob_0_to_good * prob_2_to_good)
                elif condition == "0-1":
                    individual_prob.append(prob_0_to_good * prob_1_to_good)

            else:  # This person does not have parents' data
                # The simple probability of not having any of the mutated genes
                individual_prob.append(PROBS["gene"][0])

        '''Now we compute trait probability'''
        # Find the probability that the person has the trait given that they have a certain number of the genes
        # Use what is known (or at least hypothetically) about gene number to determine probability
        if person in one_gene:
            # We want the PROBS["trait"][n][True] if person in has both n genes and happens to also have trait
            individual_prob.append(PROBS["trait"][1][person in have_trait])
        elif person in two_genes:
            individual_prob.append(PROBS["trait"][2][person in have_trait])
        else:
            individual_prob.append(PROBS["trait"][0][person in have_trait])

    '''Now we multiply through all the probabilities to compute the joint prob of all such events occurring'''
    for prob in individual_prob:
        probability = probability * prob

    return probability


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities.keys():
        # Update gene probability
        if person in one_gene:
            probabilities[person]["gene"][1] += p
        elif person in two_genes:
            probabilities[person]["gene"][2] += p
        else:
            probabilities[person]["gene"][0] += p

        # Update trait probability
        probabilities[person]["trait"][person in have_trait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    def get_normalized(vec):
        alpha = 1/(sum(vec))
        normalized = []
        for i in vec:
            normalized.append(i*alpha)
        return normalized

    for person in probabilities.keys():
        this_person = probabilities[person]

        gene_probs = [this_person["gene"][i] for i in range(3)]
        new_genes = get_normalized(gene_probs)
        for i in range(3):
            this_person["gene"][i] = new_genes[i]

        trait_probs = [this_person["trait"][True], this_person["trait"][False]]
        new_traits = get_normalized(trait_probs)
        this_person["trait"][True] = new_traits[0]
        this_person["trait"][False] = new_traits[1]


if __name__ == "__main__":
    main()