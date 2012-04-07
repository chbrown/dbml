%returns P(queryVar=queryVal | evidenceVars=evidenceVals) computed using
% Gibbs sampling
function prob = approxInf(queryVar, queryVal, evidenceVars, evidenceVals, dag, bnet, nVars)
    evidence = zeros(1, nVars);
    evidence(evidenceVars) = evidenceVals;
    unclampedIndices = find(evidence == 0);
    
    % 'zs' corresponds to all z_i's as on Bishop p. 543
    zs = ones(1, nVars);
    zs(evidenceVars) = evidenceVals; % set the evidence vars as we have them.
    
    nIterations = 10000;
    burnin = 1000;
    
    % nObservations and nSuccesses are each nVars-long, but we never access
    % the indices at evidenceVars
    nObservations = zeros(1, nVars);
    nSuccesses = zeros(1, nVars);
    
    % iterative loop
    for iteration=1:nIterations
        
        % "scan" loop
        for sample=unclampedIndices
            % 'sample' is the index of zs that we are currently sampling
            % (the i in z_\i)

            % p. 382 -- compute p(x_i|x_{\i})
            p_cond = probZiGivenE(zs, sample, dag, bnet);

            % this rand() call is the Gibbs sample
            success = rand() < p_cond;
            % success is 0-false, 1-true, so (2 - success) gets to 1-true, 2-false
            zs(sample) = 2 - success;
            
            if iteration > burnin
                nObservations(sample) = nObservations(sample) + 1;
                nSuccesses(sample) = nSuccesses(sample) + success;
            end
        end
    end
    
    % queryVal is either 1-true, or 2-false
    p_success = nSuccesses(queryVar) / nObservations(queryVar);
    %fprintf('nSuccesses=%d / nObservations=%d = %0.5f \n', nSuccesses(queryVar), nObservations(queryVar), p_success);
    if 2 - queryVal
        % if we're testing the probability of a true result
        prob = p_success;
    else
        % of the probability of a false result
        prob = 1 - p_success;
    end
end

% HW6 (4): "compute P(z_i|e) where z_i is an assignment to a single
% variable"
function prob = probZiGivenE(e, i, dag, bnet)
    % because we're only concerned with boolean values, we just test
    % against the assignment where z_i = true and then the assignment where
    % z_i = false
    varVals1 = e;
    varVals1(i) = 1;
    varVals2 = e;
    varVals2(i) = 2;
    joint1 = computeJoint(varVals1', dag, bnet);
    joint2 = computeJoint(varVals2', dag, bnet);
    prob = joint1 / (joint1 + joint2);
end
