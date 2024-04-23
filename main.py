from PIL import Image
import numpy as np

BYTE_SIZE = 8  # Assuming that everything is the size of bytes (the values of RGB and the size of chars)
BITS_IN_PIXEL = 2  # Number of encrypted bits in a pixel
MASK = (1 << BITS_IN_PIXEL) - 1  # Mask which gets us the LSB bits of a byte


def cyclic_shift(bits, size, num_of_shifts):
    none_cyclic_shift = (bits << num_of_shifts) % (1 << size)
    lost_in_shift = bits >> (size - num_of_shifts)
    return none_cyclic_shift | lost_in_shift


class Picture:

    def __init__(self, path):
        try:
            img = Image.open(path)
        except:
            raise Exception("Can't find image file")

        self.pic_data = np.array(img)

        self.h = 0
        self.w = 0
        self.d = 0

    def get_pixel(self):
        return self.pic_data[self.h][self.w][self.d]

    def next(self):
        self.d = (self.d + 1) % self.pic_data.shape[2]

        if self.d == 0:
            self.w = (self.w + 1) % self.pic_data.shape[1]

            if self.w == 0:
                self.h = (self.h + 1) % self.pic_data.shape[0]

                if self.h == 0:
                    self.h = -1
                    self.w = -1
                    self.d = -1
                    return None

        return self.get_pixel()

    def set_pixel(self, pixel):
        self.pic_data[self.h][self.w][self.d] = pixel

    def finished(self):
        return self.h == -1 and self.w == -1 and self.d == -1

    def save_image(self, path):
        img = Image.fromarray(self.pic_data)
        img.save(path, str(path.split(".")[1].upper()))


class Encryptor:

    def __init__(self, image_path, text_path):
        self.pic = Picture(image_path)

        try:
            text_file = open(text_path, 'r')
        except:
            raise Exception("Can't find text file")

        self.message = text_file.readlines()
        text_file.close()

    def enc_char(self, secret):
        shifted_secret = ord(secret)
        for i in range(int(BYTE_SIZE / BITS_IN_PIXEL)):
            if self.pic.finished():
                raise Exception("Picture too small")

            shifted_secret = cyclic_shift(shifted_secret, BYTE_SIZE, BITS_IN_PIXEL)
            old_byte = self.pic.get_pixel()
            new_byte = (old_byte & ~MASK) | (shifted_secret & MASK)
            self.pic.set_pixel(new_byte)
            self.pic.next()

    def enc_msg(self, res_path):
        for line in self.message:
            for byte in line:
                self.enc_char(byte)
            self.enc_char('\n')
        self.pic.save_image(res_path)


class Decryptor:

    def __init__(self, image_path):
        self.pic = Picture(image_path)

    def dec_char(self):
        result = 0
        for i in range(int(BYTE_SIZE / BITS_IN_PIXEL)):
            if self.pic.finished():
                raise Exception("Picture too small")

            read_byte = self.pic.get_pixel()
            result = (result << BITS_IN_PIXEL) | (read_byte & MASK)
            self.pic.next()
        return chr(result)

    def dec_msg(self, res_path):
        message = ""
        read_val = '_'
        while ord(read_val) != 0:
            read_val = self.dec_char()
            message += read_val

        result_file = open(res_path, 'w+')
        result_file.write(message)
        result_file.close()


if __name__ == '__main__':
    enc = Encryptor("./pic.png", "./text.txt")
    enc.enc_msg("res.png")

    dec = Decryptor("./res.png")
    dec.dec_msg("./res.txt")
