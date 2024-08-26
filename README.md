This is a Python based cycle accurate simulator. 

Each step in the operation of SIGMA is modeled as a function. The SIGMA has been modeled assuming the worst possible case of the hardware utilization during preprocessing before sending the corresponding elements
to flexDPEs. As SIGMA said that multicasts, multiplications and reductions are all happening in the pipelined fashion. Only those elements have pipelined in the SIGMA simulator.

Number of FlexDPU_multipliers in the FLEXDPE has been modeled with classes.

Possible assumptions made:
1) Two input OR gate in step ii, because the streaming bitmap may not always be same.
2) A set of AND gates according to each row in step ii for ANDing with OR results.
3) Approriate cycle operations have been considered for eliminating certain elements in the resultant stationary matrix.
