"""
Grayscale module
"""
import numpy as np
from PIL import Image, ImageOps


class GrayscaleImage:
    def __init__(self, nrows, ncols):
        """
        Init method
        """
        self.nrows = nrows
        self.ncols = ncols
        # Return a new array of given shape and type, filled with zeros.
        self.photo = np.zeros((self.nrows, self.ncols))

    def width(self):
        """
        Return the width of the image
        """
        return self.ncols

    def height(self):
        """
        Return the height of the image
        """
        return self.nrows

    def clear(self, value):
        """
        Clears the image
        """
        # Return a new array of given shape and type, filled with fill_value.
        self.photo = np.full((self.nrows, self.ncols), value)

    def getitem(self, row, col):
        """
        Returns the value at the given item
        """
        return self.photo[row][col]

    def setitem(self, row, col, value):
        """
        Assigns the given value to the given item
        """
        self.photo[row][col] = value

    def from_file(self, path):
        """
        Load image from file
        """
        # Create an array from the image
        self.photo = np.array(ImageOps.grayscale(Image.open(path)))

    def lzw_compression(self):
        """
        LZW compression
        """
        dict_size = 256
        dictionary = {chr(i): i for i in range(dict_size)}
        uncompressed = ""
        # 1-D array, containing the elements of the input
        for number in np.ravel(self.photo):
            uncompressed += chr(number)

        w = ""
        result = []
        for c in uncompressed:
            wc = w + c
            if wc in dictionary:
                w = wc
            else:
                result.append(dictionary[w])
                dictionary[wc] = dict_size
                dict_size += 1
                w = c
        if w:
            result.append(dictionary[w])


        result = np.array(result, dtype='uint32')
        self.compressed = result

        return result


    def lzw_decompression(self):
        """
        LZW decompression
        """
        # Importing StringIO module
        from io import StringIO

        dict_size = 256
        dictionary = {i: chr(i) for i in range(dict_size)}
        result = StringIO()

        compressed = list(self.compressed)

        w = chr(compressed.pop(0))
        result.write(w)

        for k in compressed:
            if k in dictionary:
                entry = dictionary[k]
            elif k == dict_size:
                entry = w + w[0]
            else:
                raise ValueError('Bad compressed k: %s' % k)
            result.write(entry)

            # Add w+entry[0] to the dictionary.
            dictionary[dict_size] = w + entry[0]
            dict_size += 1

            w = entry
        result = result.getvalue()

        # Creating an array from StringIO object using  ascii table
        table = {chr(i): i for i in range(dict_size)}
        string = ""
        for elem in result:
            string += str(table[elem]) + " "
        lst = string.strip().split()
        result = np.array([int(i) for i in lst], dtype="uint8")
        # Possibly need to reshape the array to the correct size of the image
        result.reshape((self.height(), self.width()))
        return result

def main():
    """
    Main function
    """
    file = r"example_image.jpg"
    image = Image.open(file)
    grayscale_image = ImageOps.grayscale(image)
    photo = GrayscaleImage(*grayscale_image.size[::-1])
    photo.from_file(file)

    compressed = photo.lzw_compression()
    decompressed = photo.lzw_decompression()

    compression_ratio = round((len(compressed) / photo.photo.size * 100), 2)
    print(f"\nCompression ratio: {compression_ratio}%\n")

    image = Image.fromarray(decompressed)
    image.show()

if __name__ == "__main__":
    main()
