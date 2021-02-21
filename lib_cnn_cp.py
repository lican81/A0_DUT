import numpy as np

class CNN:
    def __init__(self,weight,imginput,GMAX,Gmax,Gmin,p):
        self.Wm=weight.reshape(weight.shape[0]*weight.shape[1],weight.shape[2],weight.shape[3])
        self.img=imginput
        self.p=p
        self.d=imginput.shape[1]
        self.f=weight.shape[0]
        self.conv=self.Wm*(1/self.scaling())
        self.Gconv1=self.weight2conductance(self.conv,Gmax,Gmin)
        self.Gconv2=self.weightclosedp(self.conv,GMAX)
        self.imginput=self.cnn_input()
        
    
    def weight2conductance(self,Wm,Gmax,Gmin):
        Gmid=(Gmax+Gmin)/2
        Gratio=(Gmax-Gmin)/2
        Gconv=np.zeros((Wm.shape[0],Wm.shape[1],Wm.shape[2]*2))
        Gconv[:,:,::2]=Wm*Gratio+Gmid
        Gconv[:,:,1::2]=-Wm*Gratio+Gmid
        
        self.Gratio=Gratio
        return Gconv
    
    def weightclosedp(self,Wm,Gmax):
        Gconv=np.zeros((Wm.shape[0],Wm.shape[1],Wm.shape[2]*2))
        Gpos=Wm.copy()
        Gpos[Gpos<0]=0
        Gconv[:,:,::2]=Gpos*Gmax
        Gneg=Wm.copy()
        Gneg[Gneg>0]=0
        Gconv[:,:,1::2]=-Gneg*Gmax
        self.Gmax=Gmax

        return Gconv

    def scaling(self):
        MScal=np.zeros((self.Wm.shape[2],))
        
        for i in range(len(MScal)):
            MScal[i]=self.norm(self.Wm[:,:,i].reshape(-1))
                
        self.scal=MScal
        Mscal=np.tile(MScal,(self.f**2,self.Wm.shape[1],1))
        
        return Mscal
        
        
    def norm(self,vec):
        vec=vec.reshape(-1)
        vec_pos=vec.copy()
        vec_pos[vec_pos<0]=0

        vec_neg=vec.copy()
        vec_neg[vec_neg>0]=0

        scaling=max(vec_pos.max(),-vec_neg.min())
            
        return scaling   
    
    def cnn_input(self):
        matrixin=np.zeros((self.img.shape[0],self.d+self.p,self.d+self.p))
        matrixin[:,self.p//2:self.p//2+self.d,self.p//2:self.p//2+self.d]=self.img
    
        #transfer into crossbar input:
        h=self.d+self.p-self.f+1
        minput=np.zeros((self.img.shape[0],h**2,self.f**2))
        
        for k in range(self.img.shape[0]):
            for i in range(h):
                for j in range(h):
                    minput[k,i*h+j,:]=matrixin[k,i:i+self.f,j:j+self.f].reshape(-1)
    
        return minput
    
    def max_pooling(self,image_input,size=(2,2)):
        x_dim = image_input.shape[1] // size[0]
        y_dim = image_input.shape[2] // size[1]

        ch_dim = image_input.shape[0]

        image_output = np.zeros((ch_dim, x_dim, y_dim))

        for ch in range(ch_dim):
            for x in range(x_dim):
                for y in range(y_dim):
                    img_patch = image_input[ch, x*size[0]:(x+1)*size[0],
                                                y*size[1]:(y+1)*size[1]]
                    image_output[ch, x, y] = img_patch.max()

        return image_output
    
    def relu(self,x):
        return x*(x>0)
    
    def Matrixout(self,image_out,scalin,b):
        return self.relu(image_out*scalin*self.scal/self.Gratio+b)
        