import re
from mrjob.job import MRJob
from mrjob.step import MRStep
from mrjob.protocol import RawValueProtocol

class WordFrequencyMR(MRJob):
    # set the output protocol to RawValueProtocol to prevent Unicode escaping
    # link: https://mrjob.readthedocs.io/en/latest/guides/writing-mrjobs.html#job-protocols
    OUTPUT_PROTOCOL = RawValueProtocol

    # define arguments for the script:
    # context size: before and after the target word
    def configure_args(self):
        super(WordFrequencyMR, self).configure_args()
        self.add_passthru_arg(
            '--context-size', type = int, default = 3,
            help = 'Number of words to include before and after the target word as context'
        )

    def mapper_init(self):
        # precompile regex for performance
        self.word_pattern = re.compile(r'\b\w+\b')

    def mapper(self, _, line):
        try:
            # split the line by tab into filename, title, and content
            # split into at most 3 parts
            # this is how the files were combined
            parts = line.strip().split('\t', 2)  
            if len(parts) != 3:
                # skip lines that do not have exactly 3 fields
                return

            # unpack parts into filename, title and content
            filename, title, content = parts
            # remove leading and trailing whitespaces
            filename = filename.strip()
            title = title.strip()
            content = content.strip()

            # tokenize content into words, remove punctuation, convert to lowercase
            words = self.word_pattern.findall(content.lower())

            # get the context size
            context_size = self.options.context_size

            # for each word (and its index)
            for i, target_word in enumerate(words):
                # define the window for context
                start = max(0, i - context_size)
                # +1 because slice is exclusive
                end = min(len(words), i + context_size + 1) 

                # extract context words, including the target word itself
                context_words = words[start:end]

                # convert context words to a string
                context_str = ' '.join(context_words)

                # create a composite key: filename, title, word
                composite_key = f"{filename}\t{title}\t{target_word}"

                # emit the composite key and context
                yield composite_key, context_str

        except Exception as e:
            # log the error or skip the line
            print(e)
            pass

    def reducer(self, key, values):
        # initialize frequency and context list
        frequency = 0
        contexts = []

        # for each context in the values passed,
        # increment frequenct and append context to list
        for context in values:
            frequency += 1
            contexts.append(context)

        # # to avoid extremely large outputs, limit the number of contexts
        # contexts = contexts[:100]

        # Join contexts with a separator, e.g., ' | '
        contexts_joined = ' | '.join(contexts)

        # combine key and value into a single string
        # key: filename, title, word
        # value: frequency, contexts
        output_str = f"{key}\t{frequency}\t{contexts_joined}"

        # emit the final output as a single string
        yield None, output_str

    def steps(self):
        return [
            MRStep(
                mapper_init = self.mapper_init,
                mapper = self.mapper,
                reducer = self.reducer
            )
        ]

if __name__ == '__main__':
    WordFrequencyMR.run()
