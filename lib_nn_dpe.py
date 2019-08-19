import numpy as np


class NN_dpe:
    def __init__(self, weights):
        self.Mconv = weights[0].reshape(
            weights[0].shape[0]*weights[0].shape[1],
            weights[0].shape[3])

        self.Mconv = np.concatenate((self.Mconv, weights[1].reshape(1, -1)))

        self.Mfc = np.concatenate((weights[2], weights[3].reshape(1, -1)))

        self.sz_conv = [weights[0].shape[0], weights[0].shape[1]]

        self.Gconv = self.weight2conductance(self.Mconv)
        self.Gfc = self.weight2conductance(self.Mfc)

    def _dot(self, M, v):
        # return M @ v

        result = self.weight2conductance(M.T).T @ v / self.Gratio
        return result[::2] - result[1::2]

    def weight2conductance(self, Mw):
        Gmin, Gmax = 5e-6, 200e-6
        Gmid = (Gmin+Gmax)/2
        Gratio = (Gmax-Gmin)/2

        Gconv = np.zeros((Mw.shape[0], Mw.shape[1]*2))
        Gconv[:, 0::2] = Mw * Gratio + Gmid
        Gconv[:, 1::2] = -Mw * Gratio + Gmid

        self.Gratio = Gratio

        return Gconv

    def _conv_flattern(self, image_input):

        p_dim = [d // 2*2 for d in self.sz_conv]
        x_dim = image_input.shape[0] - p_dim[0]
        y_dim = image_input.shape[1] - p_dim[1]
        c_dim = image_input.shape[2]

        image_vectors = np.zeros((self.sz_conv[0]*self.sz_conv[1]+1,
                                  x_dim*y_dim*c_dim))

        i = 0
        for c in range(c_dim):
            for x in range(x_dim):
                for y in range(y_dim):

                    img_patch = image_input[x:x+self.sz_conv[0],
                                            y:y+self.sz_conv[1], c] \

                    img_patch = np.append(img_patch.reshape(-1, 1), 1)

                    image_vectors[:, i] = img_patch

                    i += 1

        return image_vectors

    def conv2D(self, image_input):
        p_dim = [d // 2*2 for d in self.sz_conv]
        x_dim = image_input.shape[0] - p_dim[0]
        y_dim = image_input.shape[1] - p_dim[1]

        image_vectors = self._conv_flattern(image_input)

        image_output = self._dot(self.Mconv.T, image_vectors)
        image_output = image_output.T.reshape(x_dim, y_dim, -1)

        return image_output

    def max_pooling(self, image_input, size=(5, 5)):

        x_dim = image_input.shape[0] // size[0]
        y_dim = image_input.shape[1] // size[1]

        ch_dim = image_input.shape[2]

        image_output = np.zeros((x_dim, y_dim, ch_dim))

        for ch in range(ch_dim):
            for x in range(x_dim):
                for y in range(y_dim):
                    img_patch = image_input[x*size[0]:(x+1)*size[0],
                                            y*size[1]:(y+1)*size[1], ch]
                    image_output[x, y, ch] = img_patch.max()

        return image_output

    def relu(self, x):
        return x * (x > 0)

    def flattern(self, image_input):
        return image_input.reshape(-1)

    def dense(self, x):
        x = np.append(x, 1)

        return self._dot(self.Mfc.T, x)

    def forward_pass(self, image_input):

        image = self.conv2D(image_input)
        image = self.relu(image)
        image = self.max_pooling(image)
        x = self.flattern(image)
        y = self.dense(x)

        return y
