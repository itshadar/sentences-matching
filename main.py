from typing import Final, Iterator, TypeAlias
from collections import namedtuple
from argparse import Namespace, ArgumentParser
from pathlib import Path
from typing_extensions import Self


# CONSTANTS
OUTPUT_FILE: Final[str] = "output.txt"

# TYPE ALIAS
Word = namedtuple("Word", ["word_index", "word_str"])


class Sentence:

    def __init__(self, words):
        self.words: list[Word] = words

    def __str__(self) -> str:
        """Return the sentence as a simple string."""
        return Sentence.get_words_string(self.words)

    def __len__(self) -> int:
        """Return the number of words the builds the sentence."""
        return len(self.words)

    @classmethod
    def create(cls: Self, line: str) -> Self:
        words = [Word(word_index, word_str) for word_index, word_str in enumerate(line.strip().split(" "))]
        return cls(words)

    @staticmethod
    def get_words_string(words: list[Word]) -> str:
        """
        Converts list of Word type to a simple string.

        :return: The sentence as a string.
        """
        return ' '.join([word.word_str for word in words])

    @staticmethod
    def parse_to_sentences(lines: list[str]) -> list[Self]:
        """
        Parses each simple string sentence into a Sentence type object.

        :param lines: A list of sentences as strings.
        :return: A list of Sentence type objects.
        """
        sentences = [Sentence.create(line) for line in lines]
        return sentences

    def get_word_str_by_index(self, index: int) -> str:
        return self.words[index].word_str

    def get_sub_sentence_words(self, start_index, end_index, pop_index=None) -> list[Word]:
        pop_index = start_index if pop_index is None else pop_index
        return self.words[start_index:pop_index] + self.words[pop_index + 1: end_index]


class Pattern:

    START_INDEX: Final[int] = 2

    def __init__(self, pattern_string, pattern_index):
        """
        Initialize a Pattern object with the given pattern string and index.

        :param pattern_string: The string pattern.
        :param pattern_index: The index of the differing word in the pattern.
        """
        self.pattern_string = pattern_string
        self.pattern_index = pattern_index

    def __eq__(self, other):
        """
        Compare if two Pattern objects are equal based on their pattern string and index.

        :param other: The other Pattern object to compare.
        :return: True if the two Pattern objects are equal, False otherwise.
        """
        return (self.pattern_string == other.pattern_string) and (self.pattern_index == other.pattern_index)

    def __hash__(self):
        return hash((self.pattern_string, self.pattern_index))

    @classmethod
    def create(cls: Self, sentence: Sentence, pattern_index: int) -> Self:
        """return pattern instance by specified pattern index within the given sentence."""
        pattern_string = Pattern.extract_pattern_string(sentence, pattern_index)
        self = cls(pattern_string, pattern_index)
        return self

    @staticmethod
    def extract_pattern_string(sentence: Sentence, pattern_index: int) -> str:
        """Extracts the pattern string by removing the word at the specified pattern index within the given sentence."""
        pattern_words: list[Word] = sentence.get_sub_sentence_words(start_index=Pattern.START_INDEX,
                                                                    end_index=len(sentence),
                                                                    pop_index=pattern_index)
        return Sentence.get_words_string(pattern_words)


class PatternCollection:

    def __init__(self):
        """
        Initialize an instance that contains patterns and their associated sentences,
        along with a set of pattern groups - patterns that have more than one associated sentence.
        """
        self._data: dict[Pattern, list[Sentence]] = dict()
        self._pattern_groups: set[Pattern] = set()

    def has_pattern(self, pattern) -> bool:
        """Check if a pattern is already found."""
        return pattern in self._data

    def add_pattern(self, new_pattern: Pattern, pattern_sentence: Sentence) -> None:
        """Add new pattern and initialize its associate sentence."""
        self._data[new_pattern] = [pattern_sentence]

    def update_pattern(self, pattern: Pattern, pattern_sentence: Sentence):
        """Update a pattern with additional pattern sentence and define it as a pattern group."""
        self._data[pattern].append(pattern_sentence)
        self._pattern_groups.add(pattern)

    def get_patterns_groups(self) -> Iterator[tuple[Pattern, list[Sentence]]]:
        """Get an iterator over the pattern groups, yielding each pattern and its associated sentences."""
        return ((pattern, self._data[pattern]) for pattern in self._pattern_groups)

    def extract_pattern_groups_output(self) -> Iterator[str]:
        """Extract from the pattern collection only the patterns that have a group of sentences."""
        for pattern, sentences in self.get_patterns_groups():
            yield PatternCollection.get_pattern_collection_paragraph(sentences, pattern.pattern_index)

    @staticmethod
    def get_pattern_collection_paragraph(sentences: list[Sentence], pattern_index: int) -> str:
        """
        Creates and returns a paragraph containing the pattern string details.

        :param sentences: A list of sentences that share the same pattern.
        :param pattern_index: The index of the differing word in the pattern.
        :return: A paragraph containing the detailed pattern string.
        """
        changing_word = ','.join([sentence.get_word_str_by_index(pattern_index) for sentence in sentences])
        return '\n'.join([str(sentence) for sentence in sentences]) + \
               f"\nThe changing word was: {changing_word}\r\n"

    @staticmethod
    def collect_patterns(sentences: list[Sentence]) -> Self:
        """
        Collects and extracts all the patterns that exist in the given sentences.

        :param sentences: A list of sentences of the Sentence data type.
        :return: A PatternCollection instance that holds:
                 1. Each pattern and its associated sentences.
                 2. Patterns that are defined as groups (having more than one associated sentence).
        """
        patterns_collection = PatternCollection()
        for sentence in sentences:

            for pattern_index in range(Pattern.START_INDEX, len(sentence)):
                pattern = Pattern.create(sentence, pattern_index)
                if patterns_collection.has_pattern(pattern):

                    # update pattern with the additional sentence that found.
                    patterns_collection.update_pattern(pattern, sentence)
                    break

                else:
                    # add new pattern to the patterns collection
                    patterns_collection.add_pattern(pattern, sentence)

        return patterns_collection


def parse_args() -> Namespace:
    """Return arguments for the program."""
    parser = ArgumentParser(description='match pattern to sentences.')
    parser.add_argument('-f', '--file', required=True, help='The file path for sentences file.')
    args = parser.parse_args()
    return args


def read_file(fp: Path) -> list[str]:
    """"Read file. Return lines of file's content."""
    try:
        with fp.open() as file:
            return file.readlines()

    except FileNotFoundError:
        raise ValueError(f"File not found: {fp}")


def write_file(fp: Path, content: Iterator[str]) -> None:
    """Write to output file."""
    with open(fp, "w") as output_file:
        output_file.writelines(content)


def main():

    # Get needed arguments for program run.
    args = parse_args()
    input_fp = Path(args.file)
    output_fp = input_fp.parent.joinpath(OUTPUT_FILE)

    # Read and parse the file content and get sentences patterns matching
    try:
        lines = read_file(input_fp)

    except ValueError as e:
        print(f"Error: {e}")
        return

    sentences: list[Sentence] = Sentence.parse_to_sentences(lines)
    patterns_collection: PatternCollection = PatternCollection.collect_patterns(sentences)
    output: Iterator[str] = patterns_collection.extract_pattern_groups_output()

    # Write the program output
    write_file(output_fp, output)


if __name__ == '__main__':
    main()

