# Twitch Timeout Battle
## Workflows
### Roulette
1. Roulette custom add redemption event received
2. rand 1 to 7
3. [Optional] Message chat with result
4. On Death:
    1. timeout user with ban function
    2. Send redemption update to FULLFILLED
5. On Survive
    1. Send redemption update to CANCELLED
6. Log event

### Uno reverse
1. Uno reverse custom add redemption event received
2. Add user and count in db
3. Send redemption update to FULLFILLED
4. Log event

### Timeout someone
1. Timeout someone custom add redemption event received
2. Get list of user watching
3. Parse message to find a user
4. No user or self
    1. Send redemption update to CANCELLED
5. User found
    1. Collect attacker uno reverse count
    2. Collect attackee uno reverse count
    3. substract min between the two to both
    4. Check winner higher number
        1. If equal attacker wins
    5. timeout loser user with ban function
    6. Update uno reverse count to both user
    7. Send redemption update to FULLFILLED
7. Write fight sequence (user 1 attacks users 2, user 2 uses uno reverse card, user 1 uses uno reverse card, user 1 wins, rip user 2)
