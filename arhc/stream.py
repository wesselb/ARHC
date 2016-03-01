class Stream:
    """
    Encapsulation of a communication channel where the number of bits to be
    read or to be written is specified.

    :param stream: Communication channel.
    :param N:      Number of bits to be read or to be written.
    """

    bitsRead = 0
    bitsWritten = 0

    def __init__(self, stream, N):
        self.stream = stream
        self.N = N

    def read(self, num=1):
        """ Read from the channel. """
        contents = self.stream.read(num)
        self.bitsRead += len(contents)
        self.observerRead(contents)
        return contents

    def write(self, string):
        """ Write to the channel. """
        self.bitsWritten += len(string)
        self.observerWrite(string)
        self.stream.write(string)
        self.stream.flush()

    def bitsLeftToRead(self):
        """ Get number of bits left to read. """
        return self.N - self.bitsRead

    def bitsLeftToWrite(self):
        """ Get number of bits left to write. """
        return self.N - self.bitsWritten

    def observerRead(self, x):
        """ Function that observes every bit that is read. """
        pass

    def observerWrite(self, x):
        """ Function that observes every bit that is written. """
        pass

    def observeRead(self, observer):
        """ Set a function that will be called when any bits are read. """
        self.observerRead = observer

    def observeWrite(self, observer):
        """ Set a function that will be called when any bits are written. """
        self.observerWrite = observer
