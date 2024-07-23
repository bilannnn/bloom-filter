import csv
import time

import mmh3
from bitarray import bitarray

from abc import abstractmethod, ABCMeta
from loguru import logger


class BloomFilterBase(metaclass=ABCMeta):

    @abstractmethod
    def add(self, url: str) -> None:
        """
        Used to add a url to the bloom filter
        :param url: url to be added
        :return: None
        """

    @abstractmethod
    def check(self, url: str) -> bool:
        """
        Used to check if a url is present in the bloom filter
        :param url: url to be checked
        :return: bool
        """

    @abstractmethod
    def check_with_percent(self, url: str) -> float:
        """
        Used to check if a url is present in the bloom filter
        :param url: url to be checked
        :return: float
        """

    @abstractmethod
    def dump_to_file(self, file_path: str) -> None:
        """
        Used to dump the bloom filter to a file
        :param file_path: file path to dump the bloom filter
        :return: None
        """

    @abstractmethod
    def setup_from_file(self, file_path: str, row_limit: int | None = 1_000,) -> None:
        """
        Used to setup the bloom filter from a file
        :param file_path: file path to setup the bloom filter
        :param row_limit: row limit to read from the file
        :return: None
        """

    @abstractmethod
    def setup_from_dump(self, file_path: str) -> None:
        """
        Used to setup the bloom filter from a dump file
        :param file_path: file path to setup the bloom filter
        :return: None
        """


class BloomFilterImpl(BloomFilterBase):

    def __init__(self,
                 bitarray_size: int = 5000,
                 layer_count: int = 10,
                 seed_start_poit: int = 41,

                 ) -> None:
        self.bitarray_size = bitarray_size
        self.layer_count = layer_count
        self.seed_start_poit = seed_start_poit

        self.bit_array = bitarray(self.bitarray_size)
        self.bit_array.setall(0)

        logger.info(
            f"Bloom filter initialized with bitarray size: {bitarray_size}, layer count: {layer_count}, seed start point: {seed_start_poit}!")

    def setup_from_file(self, file_path: str, row_limit: int | None = 1_000) -> None:
        logger.info(f"Setting up bloom filter from file: {file_path}; limit {row_limit}!")
        file_data = csv.reader(open(file_path))
        for i, row in enumerate(file_data):
            if row_limit and i >= row_limit:
                break
            self.add(row[1])

    def add(self, url: str) -> None:
        for i in range(self.layer_count):
            b = mmh3.hash(url, self.seed_start_poit + i) % self.bitarray_size
            self.bit_array[b] = 1

    def check(self, url: str, ) -> bool:
        result = [self.bit_array[mmh3.hash(url, self.seed_start_poit + i) % self.bitarray_size] for i in
                  range(self.layer_count)]

        return result.count(True) == self.layer_count

    def check_with_percent(self, url: str, ) -> float:
        result = [self.bit_array[mmh3.hash(url, self.seed_start_poit + i) % self.bitarray_size] for i in
                  range(self.layer_count)]

        return result.count(True) / self.layer_count

    def dump_to_file(self, file_path: str, ) -> None:
        logger.info(f"Dumping bloom filter to file: {file_path}!")

        with open(file_path, 'w') as file:
            for i in range(self.bitarray_size):
                file.write(str(int(self.bit_array[i])))

            logger.success(f"Dumped bloom filter to file: {file_path}!")

    def setup_from_dump(self, file_path: str, ) -> None:
        logger.info(f"Setting up bloom filter from dump file: {file_path}!")

        with open(file_path, 'r') as file:
            data = file.read()
            for i in range(self.bitarray_size):
                self.bit_array[i] = bool(int(data[i]))

        logger.success(f"Setup completed successfully!")


if __name__ == '__main__':
    # input file with data
    input_file_path = 'input_data.csv'
    # initialize bloom filter
    bloom_filter = BloomFilterImpl()
    # setup bloom filter from file
    bloom_filter.setup_from_file(input_file_path, 5000)

    # if you have dump file to initialize bloom filter from it
    # you can use setup_from_dump method
    # bloom_filter.dump_to_file('bloom_filter_bit_array.txt')

    # dump bloom filter to file for future use
    bloom_filter.dump_to_file(f'bloom_filter_bit_array_{bloom_filter.layer_count}_{bloom_filter.bitarray_size}.txt',)

    while True:
        time.sleep(0.1)
        input_url = input("Enter the url to check: ")
        if input_url == "exit":
            break
        logger.info(f"Checking url: {input_url}!")
        if bloom_filter.check(input_url):
            logger.exception(f"Dangerous...do not proceed with {input_url} further!")
        else:
            logger.success(f"Can proceed further with {input_url}!")
