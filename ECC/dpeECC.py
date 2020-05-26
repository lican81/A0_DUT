import numpy as np


class dpeECC:
    def __init__(self, A, delta=0.01, Delta=0.2):
        '''
        A is the original matrix
        '''
        self.A = A
        self.m = A.shape[0]
        self.k = A.shape[1]
        self.delta = delta
        self.Delta = Delta

        assert Delta >= delta * 6

        self._init_encoder()

    def _init_encoder(self):
        k = self.k

        r = max(2*self.k//(np.floor(self.Delta/(2*self.delta))-2),
                np.ceil(np.sqrt(self.k+1))+1)
        r = int(r + r % 2)

        # Initialze the parity checking matrix and syndrome look up
        # matrix
        n = k + r
        self.H = np.zeros((r, n), dtype=np.int)
        self.Lookup = np.zeros((r, r), dtype=np.int)

        # Prepare Circile
        Circle = np.zeros((r-1), dtype=np.int)
        Circle[0] = 1

        for i in range(1, r//2):
            Circle[i] = i*2
            Circle[r-1-i] = i*2+1

        # Preprocess
        phase = 1
        parity = 1
        h = 0

        for j in range(k):
            pos0 = 0 if h == 0 else Circle[(phase+h) % (r-1)]
            pos1 = Circle[(phase + r-1 - h) % (r-1)]

            # Make sure pos1 > pos0
            if pos0 > pos1:
                pos0, pos1 = pos1, pos0

            self.H[pos0][j] = 1
            self.H[pos1][j] = parity

            if parity > 0:
                self.Lookup[pos0][pos1] = j
            else:
                self.Lookup[pos1][pos0] = j

            h += 1
            if h >= r/2:
                h = 0
                parity = - parity

                if parity > 0:
                    phase += 1

                # The number of non-zero elements is less than
        # $ ceil(2k/r)
        # n_scale = np.ceil(2*self.k/r)
        # self.H = self.H / n_scale

        for j in range(r):
            if j % 2 == 0:
                self.H[j][j+k] = 1
                self.H[j+1][j+k] = 1
                self.Lookup[j][j+1] = k+j
            else:
                self.H[j-1][j+k] = 1
                self.H[j][j+k] = -1
                self.Lookup[j][j-1] = k+j

        self.Weight = np.sum(abs(self.H), axis=1) * self.delta
        self.r = r
        self.n = n

    def encode(self) -> np.ndarray:
        '''
        Return the encoded array
        '''
        S = self.H[:, :self.k] @ self.A.T
        S = S.T

        A2 = np.empty((self.m, self.r))
        A2[:, 0::2] = - (S[:, ::2] + S[:, 1::2]) / 2
        A2[:, 1::2] = - (S[:, ::2] - S[:, 1::2]) / 2

        return np.concatenate((self.A, A2), axis=1)

    def decode_w_syndrome(self, S):
        pos = np.where(abs(S) > self.Weight)[0]

        low, high = (0, 0)

        if len(pos) == 0:
            # No error is detected
            location = -1
        elif len(pos) == 1:
            # Error detected, but too small to be located
            location = -2

            low = abs(S[pos[0]]) - self.Weight[pos[0]]

            high = 0.0
            for i in range(self.r):
                if i != pos[0]:
                    high = max(high, abs(S[i] + self.Weight[i]))

        elif len(pos == 2):
            # Try to decode the error
            if np.sign(S[pos[0]]) * np.sign(S[pos[1]]) >= 0:
                location = self.Lookup[pos[0]][pos[1]]
            else:
                location = self.Lookup[pos[1]][pos[0]]

            T0 = self.H[pos[0]][location] * S[pos[0]]
            T1 = self.H[pos[1]][location] * S[pos[1]]

            low = max(T0 - self.Weight[pos[0]], T1 - self.Weight[pos[1]])
            high = min(T0 + self.Weight[pos[0]], T1 + self.Weight[pos[1]])

        else:
            # Unexpected error
            location = -99

        return location, (low, high)

    def decode(self, y):
        '''
        Decode the error
        '''
        S = self.H @ y

        return self.decode_w_syndrome(S)

        

