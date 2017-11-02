from fuzzywuzzy import fuzz

def spellcheck(attempt, real, threshold):
    '''Returns a highest scoring "attempt" match
    against "real" spelling over the "threshold"'''
    if type(real) == list or type(real == dict):
        score_list = []
        for key in real:
            check_score = fuzz.ratio(key, attempt)
            if check_score >= threshold:
                score_list.append((key,  check_score))
        if score_list:
            winner = max(score_list, key=lambda score:score[1])
            return(winner[0])
    else:
        check_score = fuzz.ratio(attempt, real)
        if check_score >= threshold:
            return real

