# import pandas as pd
import numpy as np



# Unified Model
U=24.1
tau_la=4.06*24*60  #4.06
tau_w=40*60
tau_s=1*60  #8/3
#s_e= U/5



def sleep_new(t, t0=0, tau_s=tau_s, tau_la=tau_la, U=U, S0=0, L0=0, isFD=False):
    
    
    #print(S0)
    L_t = L0*np.exp(-(t-t0)/tau_la) - 2*U*(1-np.exp(-(t-t0)/tau_la))
    S_t = S0* np.exp(-(t-t0)/tau_s) - 2*U*(1-np.exp(-(t-t0)/tau_s))+(tau_la*(L0+2*U)/(tau_la-tau_s))*(np.exp(-(t-t0)/tau_la)-np.exp(-(t-t0)/tau_s))
    
    if(isFD == True):
      L_t = L0*np.exp(-(t-t0)/tau_la) - 1.4*U*(1-np.exp(-(t-t0)/tau_la))
      S_t = S0* np.exp(-(t-t0)/tau_s) - 1.4*U*(1-np.exp(-(t-t0)/tau_s))+(tau_la*(L0+1.4*U)/(tau_la-tau_s))*(np.exp(-(t-t0)/tau_la)-np.exp(-(t-t0)/tau_s))
    
    return S_t, L_t
    
def awake_new(t, t0=0,tau_w=tau_w,tau_la=tau_la, U=U,S0=0, L0=0):
    
    
    
    S_t = U-np.exp(-(t-t0)/tau_w)*(U-S0)
    L_t = U-np.exp(-(t-t0)/tau_la)*(U-L0)
    #L_t=0
    
    
    #eff_t= (1-np.exp(-(S_t/s_e)))*100
    
    return S_t, L_t



def simulate_Unified(t_awake, t_sleep, S0,L0,t0, Forced=False):
    
    
    
    wake_times = np.linspace(t0,(t0+t_awake), t_awake+1)
    #print(wake_times) 
    
    
    
    res_awake = [awake_new(i, t0=t0, S0=S0, L0=L0) for i in wake_times] 
    s_awake, l_awake = list(map(list, zip(*res_awake)))

    
    
    
    S0 = s_awake[-1]
    #print(S0)
    L0 = l_awake[-1]
    t0 = wake_times[-1]
    
    
    
    sleep_times = np.linspace(t0,(t0+t_sleep), t_sleep+1)
     
    res_sleep = [sleep_new(i, t0=t0, S0=S0, L0=L0, isFD=Forced) for i in sleep_times] 
    
    
    
    s_sleep, l_sleep = list(map(list, zip(*res_sleep)))
    
    #eff_sleep= [eff]*len(sleep_times)
    
    return list(wake_times)+list(sleep_times),s_awake+s_sleep, l_awake+l_sleep



