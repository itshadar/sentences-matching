import argparse
import os

# CONSTANTS
OUTPUT_FILE = "output.txt"

# TYPE ALIAS
Word = tuple[int, str] # tuple of word's index and word's string
Sentence = list[Word]


def parse_args() -> argparse.Namespace:
    """Return arguments for the program. """
    parser = argparse.ArgumentParser(description='match pattern to sentences.')
    parser.add_argument('-f', '--file', required=True, help='The file path for sentences file.')
    args = parser.parse_args()
    return args


def convert_to_string(sentence: Sentence) -> str:
    """
    Covert Sentence type to a simple string.
    :param sentence: as a Sentence type.
    :return: sentence as a string.
    """
    return ' '.join([word[1] for word in sentence])


def parse_sentences(content: list[str]) -> list[Sentence]:
    """
    Parse each simple string sentence to Sentence type object.
    :param content: list of sentences as a string type
    :return: list of Sentences type objects
    """
    sentences = [[(i, word) for i, word in enumerate(line.strip().split(" "))] for line in content]
    return sentences


def read_file(fp: str) -> list[str]:
    """ Read file. Return lines of file's content. """
    try:
        with open(fp, 'r') as file:
            return file.readlines()

    except FileNotFoundError as err:
        print("ERROR:", err.strerror)
        exit(err.errno)


def write_file(fp: str, content: list[str]) -> None:
    """Write to output file."""
    with open(fp, "w") as output_file:
        output_file.writelines(content)


def get_pattern_paragraph(sentences: list[Sentence], pattern_index: int) -> str:
    """
    Create and return the pattern string paragraph.
    :param sentences: all the sentences who share the pattern
    :param pattern_index: The different word's index of the pattern
    :return: pattern string paragraph.
    """
    changing_word = ','.join([sentence[pattern_index][1] for sentence in sentences])
    return '\n'.join([convert_to_string(sentence) for sentence in sentences]) + \
           f"\nThe changing word was: {changing_word}\r\n"


def sentences_grouping(sentences: list[Sentence]) -> list[str]:
    """
    Grouping sentences who share the same pattern.
    :param sentences: list of sentences to search for common pattern.
    :return: list of patterns and the sentences matching it that were found.
    """
    sentences_patterns = []

    for index, sentence in enumerate(sentences):

        # Initialize pattern properties - changing pattern index and sentences group.
        pattern_index = -1
        pattern_group = [sentence]

        for sentence_2 in sentences[index+1:]:

            # Get the difference between the sentences pattern
            diff = list(set(sentence[2:]).difference(sentence_2[2:]))

            # Check if the difference is matching to a new/exist pattern
            if len(diff) == 1 and (pattern_index == -1 or diff[0][0] == pattern_index):

                # Save pattern changing word index
                pattern_index = diff[0][0]
                pattern_group.append(sentence_2)

                # Each sentence belongs to a single pattern
                sentences.remove(sentence_2)

        # Check if pattern were found for sentence
        if pattern_index != -1:

            # Convert pattern group to paragraph format
            sentences_patterns.append(get_pattern_paragraph(pattern_group, pattern_index))

    return sentences_patterns


def main():

    # Get needed arguments for program run.
    args = parse_args()
    input_fp = os.path.abspath(args.file)
    output_fp = os.path.join(os.path.dirname(input_fp), OUTPUT_FILE)

    # Read and parse the file content and get sentences patterns matching
    lines = read_file(input_fp)
    sentences = parse_sentences(lines)
    sentences_groups = sentences_grouping(sentences)

    # Write the program output
    write_file(output_fp, sentences_groups)


if __name__ == '__main__':
    main()

