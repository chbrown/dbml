%returns P(queryVar=queryVal | evidenceVars=evidenceVals) computed using
%BNT junction tree inference algorithm. the probability it computes is
%exact.
%see example of usage in hw6.m
function prob = exactInf(queryVar, queryVal, evidenceVars, evidenceVals, dag, bnet, numVars)
    engine = jtree_inf_engine(bnet);
    evidence = cell(1,numVars);
    numEvidenceVars = size(evidenceVars,2);
    for i = 1:numEvidenceVars
        evidence{evidenceVars(i)} = evidenceVals(i);
    end
    [engineWithEv, logLike] = enter_evidence(engine, evidence);
    marg = marginal_nodes(engineWithEv,queryVar);
    prob = marg.T(queryVal);
end

