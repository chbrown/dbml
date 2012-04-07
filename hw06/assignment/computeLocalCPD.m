%returns P(queryVar=queryVal | parentVars=parentVals)
%where parentVals(i) contains the value of the i'th parent variable
%for example, the first parent of var 3 is 1
%the second parent of var 3 is 2
%see example of usage in computeJoint.m
function prob = computeLocalCPD(queryVar,queryVal,parentVals,bnet)
    %parents = find(dag(:,var));
    cpt = CPD_to_CPT(bnet.CPD{queryVar});
    if size(parentVals,1) == 0
        prob = cpt(queryVal);
    elseif size(parentVals,1) == 1
        prob = cpt(parentVals(1),queryVal);
    elseif size(parentVals,1) == 2
        prob = cpt(parentVals(1),parentVals(2),queryVal);
    elseif size(parentVals,1) == 3
        prob = cpt(parentVals(1),parentVals(2),parentVals(3),queryVal);        
    end
end

