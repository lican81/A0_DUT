import pylab as plt
import numpy as np
plt.figure(6,figsize=(8,6))
plt.clf()
T_step=2e-9 # in s
number_of_bits_N=np.linspace(1,1000,100)
number_of_bits_N_l=np.linspace(1,2200,100)
number_of_bits_prime=number_of_bits_N/2
#source RSA-numbers: https://en.wikipedia.org/wiki/RSA_numbers#RSA-250
#plt.semilogy(problem_and_sol_arr[:,0],2**(problem_and_sol_arr[:,0])/2.,"orange",label="Sample $\in[1..2^{ceil(log2(N)/2)}]$")
# ..-1 because 1 is not our prime number
#plt.semilogy(problem_and_sol_arr[:,0],(2**(problem_and_sol_arr[:,0])/2.+1)//2-1,"k",label="Sample odd nrs $\in[3..2^{ceil(log2(N)/2)}]$")
#plt.semilogy(problem_and_sol_arr[:,0],problem_and_sol_arr[:,-1]**.5,"k--",label=r"Count up to $N^{1/2}$")
#plt.semilogy(problem_and_sol_arr[:,0],np.floor(problem_and_sol_arr[:,-1]**.5+1)//2-1,"k--",label=r"Count odd nrs.>1 up to $N^{1/2}$")
#plt.loglog(number_of_bits_N,T_step*2**(number_of_bits_prime-2),":",color="gray",label=r"ref. Henelius random")
#plt.semilogy(data_arr_nft2[:,0],data_arr_nft2[:,1],"r.-",label=r"|N mod p|")
#plt.semilogy(data_arr_Eft1[:,0],data_arr_Eft1[:,1],"b.-",label=r"|N-pq|")
plt.loglog(number_of_bits_N,T_step*0.58*2**(number_of_bits_prime-2),"-",label=r"Estimated scaling of mem-HNN (idealized architecture)")
plt.loglog(number_of_bits_N_l,np.ones_like(number_of_bits_N)*1e-3,"-.",color="grey",label=r"1 millisecond")
plt.loglog(number_of_bits_N_l,np.ones_like(number_of_bits_N),":",color="grey",label=r"1 second")
plt.loglog(number_of_bits_N_l,np.ones_like(number_of_bits_N)*3600,":",color="k",label=r"1 hour")
#plt.loglog(number_of_bits_N,np.ones_like(number_of_bits_N)*3600*24,"-.",color="k",label=r"1 day")
plt.loglog(number_of_bits_N_l,np.ones_like(number_of_bits_N)*3600*24*365,"--",color="k",label=r"1 year")
plt.loglog(number_of_bits_N_l,np.ones_like(number_of_bits_N)*435196800000000000,"-",color="gray",label=r"Age of the universe")
#special points: 330; https://en.wikipedia.org/wiki/RSA_numbers#RSA-100
plt.loglog([330],[72*60],"o",color="red",label=r"RSA-100; 72m")#RSA-100
plt.loglog([795],[900*3600*24*365],"v",color="purple",label=r"RSA-240; 900 CPU years")#RSA-250
plt.loglog([829],[2700*3600*24*365],"^",color="orange",label=r"RSA-250; 2700 CPU years")#RSA-250
plt.loglog([2048],[3600*8],"D",color="green",label=r"RSA-2048; Est. quantum = 8h")#RSA-250
#plt.loglog([829],[2700*3600*24*365],"^",color="orange",label=r"RSA-250; 2700 CPU years")#RSA-250
#2700

plt.xlabel("Number of bits")
plt.ylabel("Calculation time (s)")
#plt.ylabel("Number of iterations")
ylim_val=plt.gca().get_ylim()
plt.loglog([2048,2048],[ylim_val[0],ylim_val[-1]],":",color="green",label=r"Target: RSA-2048")#RSA-250
plt.xlim(number_of_bits_N_l[0],number_of_bits_N_l[-1])
plt.ylim(ylim_val[0],ylim_val[-1]/1e10)
leg=plt.legend(loc=0)
leg.draw_frame(False)
plt.savefig("computation_time_for_prime_factorization.pdf")
plt.savefig("computation_time_for_prime_factorization.png")


plt.show()