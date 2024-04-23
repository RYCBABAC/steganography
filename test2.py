from PIL import Image
import numpy as np

BYTE_SIZE = 8  # Assuming that everything is the size of bytes (the values of RGB and the size of chars)
BITS_IN_PIXEL = 2  # Number of encrypted bits in a pixel
MASK = (1 << BITS_IN_PIXEL) - 1  # Mask which gets us the LSB bits of a byte


def cyclic_shift(bits, size, num_of_shifts):
    none_cyclic_shift = (bits << num_of_shifts) % (1 << size)
    lost_in_shift = bits >> (size - num_of_shifts)
    return none_cyclic_shift | lost_in_shift

class Encryptor:

    def __init__(self, image_path, text_path):
        self.img = Image.open(image_path).copy()
        self.x = 0
        self.y = 0
        self.c = 0
        self.cur_pixel = list(self.img.getpixel((self.x,self.y)))

        try:
            text_file = open(text_path, 'r')
        except:
            raise Exception("Can't find text file")

        self.message = text_file.readlines()
        text_file.close()

    def finished(self):
        return self.c == -1

    def set_pixel(self):
        self.img.setpixel((self.x, self.y), tuple(self.cur_pixel))

    def get_current_byte(self):
        if self.c < 2:
            self.c += 1
        else:
            self.c = 0
            self.set_pixel()

            if self.y < self.img.size[1]-1:
                self.y += 1
            elif self.x < self.img.size[0]-1:
                self.x += 1
                self.y = 0
            else:
                self.c = -1
                return None
            self.cur_pixel = self.img.getpixel((self.x,self.y))

        return self.cur_pixel[self.c]

    def set_byte(self, byte):
        self.cur_pixel[self.c] = byte

    def enc_char(self, secret):
        shifted_secret = ord(secret)
        for i in range(int(BYTE_SIZE / BITS_IN_PIXEL)):
            shifted_secret = cyclic_shift(shifted_secret, BYTE_SIZE, BITS_IN_PIXEL)
            old_byte = self.get_current_byte()
            if old_byte is None:
                raise Exception("Picture too small")
            new_byte = (old_byte & ~MASK) | (shifted_secret & MASK)
            self.set_byte(new_byte)

    def enc_msg(self, res_path):
        for line in self.message:
            for byte in line:
                self.enc_char(byte)
            self.enc_char('\n')
        self.img.save(res_path, str(res_path.split(".")[1].upper()))




'''
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
        read_val ='_'
        while ord(read_val) != 0:
            read_val = self.dec_char()
            message += read_val

        result_file = open(res_path, 'w+')
        result_file.write(message)
        result_file.close()
'''

if __name__ == '__main__':
    enc = Encryptor("pic.jpg", "text.txt")
    enc.enc_msg("res.jpg")

    #dec = Decryptor("./res.jpg")
    #dec.dec_msg("./res.txt")