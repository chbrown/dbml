%this is the main driver code for HW6 which you should build on.

%In the following code '1' denotes TRUE and '2' denotes FALSE.
%the code to build the BBN is from 
%https://patterns.enm.bris.ac.uk/courses/artificial_intelligence/2009/lab3

%The following code makes use of the Bayes Net toolbox in order to create
%the Bayesian Belief Network of page 494, Figure 14.2 (Artificial 
%Intelligence: A modern approach).
%
%         --------
%         TOPOLOGY
%         --------
%     (1)         (2)
%   burglary  earthquake
%       \         /
%        \       /  
%         \     /
%          >(3)<
%          alarm
%          /   \
%         /     \
%        /       \
%       <         >   
%  john_calls  mary_calls
%      (4)        (5)
%

%number of nodes in our graphical model
N = 5;
%the directed acyclic graph (dag) is defined as a NxN matrix
dag = zeros(N,N);

%we assign an id to each node - the nodes must be numbered in topological 
%order, i.e. ancestors before descendants
burglary = 1; 
earthquake = 2; 
alarm = 3; 
john_calls = 4; 
mary_calls = 5;

%define the connections of the nodes 
dag(burglary, alarm) = 1; %draw an arrow from burglary node to alarm node
dag(earthquake, alarm) = 1; 
dag(alarm, [john_calls mary_calls]) = 1; %draw 2 arrows from alarm to john_calls and mary_calls

%specify the node structure
%all the nodes are discrete, i.e. we can enumerate their possible states
discrete_nodes = [1 2 3 4 5];
%each node can take two possible values/states
node_sizes = [2 2 2 2 2];
%which nodes do we observe? At the moment, none!
onodes = [];

nodeLabels = {'burglary','earthquake','alarm','john_calls', 'mary_calls'};

%create the Bayesian network
bnet = mk_bnet(dag, node_sizes,'names', nodeLabels,'discrete', discrete_nodes, 'observed', onodes);

%define the network's parameters by creating Conditional Probability
%Distributions (or Tables) (CPDs or CPTs)
%'1' denotes TRUE and '2' denotes FALSE -- MATLAB does not use '0' as an index
CPT_burglary = zeros(2,1);
CPT_burglary(1) = 0.001; CPT_burglary(2) = 0.999;

CPT_earthquake = zeros(2,1);
CPT_earthquake(1) = 0.002; CPT_earthquake(2) = 0.998;

%everything is being carried out in topological order (we have defined the
%topology and the order of the nodes in the beginning), e.g.
%CPT_alarm(1,2,1) = Pr(alarm = true | burglary = true, earthquake = false)
CPT_alarm = zeros(2,2,2);
CPT_alarm(1,1,1) = 0.95; CPT_alarm(1,1,2) = 0.05;
CPT_alarm(1,2,1) = 0.94; CPT_alarm(1,2,2) = 0.06;
CPT_alarm(2,1,1) = 0.29; CPT_alarm(2,1,2) = 0.71;
CPT_alarm(2,2,1) = 0.001; CPT_alarm(2,2,2) = 0.999;

CPT_john_calls = zeros(2,2);
CPT_john_calls(1,1) = 0.9; CPT_john_calls(1,2) = 0.1;
CPT_john_calls(2,1) = 0.05; CPT_john_calls(2,2) = 0.95;

CPT_mary_calls = zeros(2,2);
CPT_mary_calls(1,1) = 0.7; CPT_mary_calls(1,2) = 0.3;
CPT_mary_calls(2,1) = 0.01; CPT_mary_calls(2,2) = 0.99;

%insert the tables in the BBN
bnet.CPD{burglary} = tabular_CPD(bnet, burglary, CPT_burglary);
bnet.CPD{earthquake} = tabular_CPD(bnet, earthquake, CPT_earthquake);
bnet.CPD{alarm} = tabular_CPD(bnet, alarm, CPT_alarm);
bnet.CPD{john_calls} = tabular_CPD(bnet, john_calls, CPT_john_calls);
bnet.CPD{mary_calls} = tabular_CPD(bnet, mary_calls, CPT_mary_calls);

%we can draw the topology of the graph 
%G = bnet.dag;
%draw_graph(G,nodeLabels);

local = computeLocalCPD(burglary,1,[],bnet);
allVals = zeros(N,1);
allVals(burglary) = 1;
allVals(earthquake) = 2;
allVals(alarm) = 1;
allVals(john_calls) = 1;
allVals(mary_calls) = 1;
joint = computeJoint(allVals, dag, bnet);
groundTruth = 0.001 * 0.998 * 0.94 * 0.9 * 0.7;
assert(joint == groundTruth);

%two examples of how to compute conditional probabilities using 
%exact inference using the provided exactInf function

%compute p(burglary=1 | alarm=1) 
evidenceVars = [alarm];
evidenceVals = [1];
queryVar = burglary;
queryVal = 1;
p1  =  exactInf(queryVar, queryVal, evidenceVars, evidenceVals, dag, bnet, N);
p1a = approxInf(queryVar, queryVal, evidenceVars, evidenceVals, dag, bnet, N);

%compute p(burglary=1 | earthquake=1, alarm=1)
queryVar = burglary;
queryVal = 1;
evidenceVars = [earthquake, alarm];
evidenceVals = [1,1];
p2 = exactInf(queryVar, queryVal, evidenceVars, evidenceVals, dag, bnet, N);

%the provided function computeJoint will be helpful when doing gibbs
%sampling.

%you are welcome to use the following experiment-running and plotting code.
%of course, you'll need to write your own approxInf function.
numProblems = 20;
exactProbs = zeros(numProblems,1);
approxProbs = zeros(numProblems,1);
for i=1:numProblems
    randVars = randsample(N,3,false);
    randVals = randsample(2,3,true);
    queryVar = randVars(1);
    queryVal = randVals(1);
    evidenceVars = randVars(2:end)';
    evidenceVals = randVals(2:end)';
    % exactProbs takes some evidence, a particular variable, and returns
    % the probability of that variable taking some particular value
    exactProbs(i)  =  exactInf(queryVar, queryVal, evidenceVars, evidenceVals, dag, bnet, N);
    approxProbs(i) = approxInf(queryVar, queryVal, evidenceVars, evidenceVals, dag, bnet, N);
    fprintf('exact = %0.5f, approx = %0.5f\n', exactProbs(i), approxProbs(i));
    if exactProbs(i) - approxProbs(i) > 0.5
        break
    end
end

difs = exactProbs - approxProbs;
bar(difs);
title('Performance of approximate inference on random problems');
xlabel('Problem number');
set(gca,'XTick', 1:numProblems);
set(gca, 'YTickLabel', num2str(difs, '%0.5f'));
ylabel('P_{exact} - P_{approx}');
print('-dpng','hw6-plot.png')


