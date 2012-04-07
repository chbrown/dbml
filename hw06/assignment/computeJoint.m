%returns the joint probability of an assignment of values to all variables 
%varVals(i) should contain the value for variable i
%see example of usage in hw6.m
function prob = computeJoint(varVals, dag, bnet)
    prob = 1;
    numVars = size(varVals,1);
    for varNum = 1:numVars
        parents = find(dag(:,varNum));
        parentVals = varVals(parents);
        prob = prob * computeLocalCPD(varNum,varVals(varNum),parentVals,bnet);
    end
end

