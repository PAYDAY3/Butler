def greedy_activity_selection(start, finish):
    n = len(start)
    if n <= 0:
        return []

    activities = []
    sorted_activities = sorted(zip(start, finish), key=lambda x: x[1])
    
    activities.append(sorted_activities[0])
    last_finish_time = sorted_activities[0][1]

    for i in range(1, n):
        if sorted_activities[i][0] >= last_finish_time:
            activities.append(sorted_activities[i])
            last_finish_time = sorted_activities[i][1]

    return activities
