from ortools.sat.python import cp_model


def main(playerlist):
    list1 = list(playerlist.keys())
    phase = ['pp', 'mid', 'death']
    costs = []
    for i in list1:
        ph = []
        for j in phase:
            if j == 'pp':
                b = round(((-15*playerlist[i]['bowl'][j]['wkt']) + (playerlist[i]['bowl'][j]['eco']/6)), 4)
                for k in range(6):
                    ph.append(b)
            elif j == 'mid':
                b = round(((-15*playerlist[i]['bowl'][j]['wkt']) + (2*playerlist[i]['bowl'][j]['eco']/6)), 4)
                for k in range(10):
                    ph.append(b)
            else:
                for k in range(4):
                    if ((playerlist[i].get('role', None) == 'SPIN') or (playerlist[i].get('role', None) == 'PARTSPIN')):
                        six = k*0.35
                        eco = ((playerlist[i]['bowl'][j]['eco']/6) + (playerlist[i]['bowl'][j]['6']*six*6)) / (1 + (playerlist[i]['bowl'][j]['6']*six))
                        b = round(((-15*playerlist[i]['bowl'][j]['wkt']) + (2*eco)), 4)
                    else:
                        b = round(((-15*playerlist[i]['bowl'][j]['wkt']) + (2*playerlist[i]['bowl'][j]['eco']/6)), 4)
                    ph.append(b)
        costs.append(ph)

    players = len(costs)
    overs = len(costs[0])

    solver = cp_model.CpModel()

    x = []
    for i in range(players):
        t = []
        for j in range(overs):
            t.append(solver.NewBoolVar(f'x[{i},{j}]'))
        x.append(t)

    for i in range(players):
        solver.Add(sum([x[i][j] for j in range(overs)]) <= 4)

    for i in range(players):
        for j in range(overs-1):
            solver.AddImplication(x[i][j], x[i][j+1].Not())

    for j in range(overs):
        solver.Add(sum([x[i][j] for i in range(players)]) == 1)


    objective_terms = []
    for i in range(players):
        for j in range(overs):
            objective_terms.append(costs[i][j] * x[i][j])
    solver.Minimize(sum(objective_terms))

    solve = cp_model.CpSolver()
    status = solve.Solve(solver)

    bowlingOrder = []
    for i in range(overs):
                for j in range(players):
                    if solve.BooleanValue(x[j][i]):
                        bowlingOrder.append(list1[j])

    return bowlingOrder


if __name__ == '__main__':
    pass
