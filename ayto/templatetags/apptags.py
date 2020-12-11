from django import template

register = template.Library()


@register.filter
def pdb(item, item2=None):
    """ Helper for dropping into PDB from a template
    """
    import pdb
    pdb.set_trace()

@register.filter
def should_print_week(week1, week2):
    should_print_week = False
    if week1.week_number == 1 and week2.week_number == 1:
        should_print_week = True
    elif week1 == week2:
        should_print_week = False
    elif week1.week_number > week2.week_number:
        should_print_week = True
    return should_print_week


@register.filter
def overlaps_for_participant(weekly_overlaps, participant):
    overlaps_for_participant = {}
    for week, overlaps in weekly_overlaps.items():
        participant_in_matches = False
        for overlap in overlaps:
            if participant in [overlap.participant1, overlap.participant2]:
                participant_in_matches = True
        if participant_in_matches:
            overlaps_for_participant[week] = overlaps
    return overlaps_for_participant

@register.filter
def get_overlaps(week1, week2):
    overlaps = []
    if week1.matchup_set:
        compare_matchups = []
        for matchup in week2.matchup_set.all():
            compare_matchups.append(matchup.matchup)
        if compare_matchups:
            for matchup in week1.matchup_set.all():
                if matchup.matchup in compare_matchups:
                    overlaps.append(matchup)
    return overlaps

@register.filter
def get_mismatches(week1, week2):
    mismatches = []
    if week2.matchup_set.count() > 0:
        compare_matchups = []
        for matchup in week2.matchup_set.all():
            compare_matchups.append(matchup.matchup)
        for matchup in week1.matchup_set.all():
            if matchup.matchup  not in compare_matchups:
                mismatches.append(matchup)
    return mismatches
