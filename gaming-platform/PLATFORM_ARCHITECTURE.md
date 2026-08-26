# Two Feather Games & Charity: Complete Platform Architecture
## Entertainment Gaming + Donation-Driven Prize Model

---

## EXECUTIVE SUMMARY

**Platform Model**: Players donate to nonprofit, receive free social coins, play games, win real prizes.

- **GC (Gaming Coins)**: Purchased with real money, entertainment-only (no withdrawal)
- **SC (Social Coins)**: Free, given as gift when donating to Two Feathers Nationals
- **Prizes**: Real USD/gift cards won by playing with SC
- **Charity**: 60% of GC revenue + 100% of partner 70/30 split goes to nonprofit

---

## SECTION 1: CURRENCY SYSTEM

### 1.1 Gaming Coins (GC)

**Purpose**: Entertainment play currency

**Acquisition**:
- Purchase: $4.99, $9.99, $24.99, $49.99, $99.99 packs
- Bonus: First-time player gets 5,000 GC free (promo)

**Usage**:
- Wager on any game (proprietary or partner)
- No withdrawal
- No prize redemption
- Expires if account inactive for 180 days

**Mechanics**:
- Win = GC stays in account for re-play
- Lose = GC spent, gone
- No accumulation of "real value"

**Legal Stance**: "Entertainment chips — like a Vegas slot machine. Fun, but not real money."

---

### 1.2 Social Coins (SC)

**Purpose**: Prize-earning currency

**Acquisition**:
- **Primary**: Donation to Two Feathers Nationals
  - Donate $10 USD → Receive 10,000 SC (1:1 ratio, user-friendly)
  - Tax-deductible receipt issued by nonprofit
- **Secondary**: Occasional bonuses or promos (rare)
  
**Usage**:
- Wager on any game (proprietary or partner)
- **Wins are real**: SC winnings convert to actual USD/gift cards
- No expiration (permanent gift)
- Can re-wager winnings

**Mechanics**:
- Win $25 SC → Redeem for $25 Starbucks card or PayPal
- Win $5 SC → Keep playing or cash out
- Can donate SC back to nonprofit (meta engagement)

**Legal Stance**: "Free gift from nonprofit. Wins are real prizes earned through entertainment."

---

### 1.3 Prizes

**Available Redemptions**:
- USD via PayPal (minimum $5)
- Gift cards: Starbucks, Amazon, Best Buy, etc. ($5-$100)
- Prepaid debit cards (via partner processor)
- Donate back to nonprofit (generates tax receipt)

**Prize Pool Funding**:
- 40% of GC revenue reserved for prize redemption
- Example: $10,000 GC revenue/month → $4,000 prize pool
- Ensures sustainability without "house always loses"

**Redemption Process**:
1. Player clicks "Redeem Prize"
2. Selects prize type and amount
3. Completes verification (ID + address for >$100 redemptions)
4. Prize delivered within 3-5 business days
5. Tax receipt auto-generated (1099-MISC for >$600/year)

---

## SECTION 2: GAME ARCHITECTURE

### 2.1 Game Categories (50 Total)

#### **A. PROPRIETARY GAMES (30 games — 100% to charity)**

**Slot Engine A: Wild Multiplier (6 games)**
- `RedFeatherWild` — 5-reel, 1-3 random wilds/spin, 1-5x multiplier
- `BuffaloSpin` — 5-reel, expanding wild, re-spins
- `EagleSkyWild` — 5-reel, roaming wild, moving left/right
- `SacredWildExpand` — 5-reel, expanding wild on all reels
- `CouncilWildMult` — 5-reel, stacked wild, chain multiplier
- `RiverWild` — 5-reel, wild substitute + bonus coins

**Slot Engine B: Free Spin Scatter (6 games)**
- `TwoFeatherBonus` — 5-reel, 3+ scatter = 12 free spins, 2x multiplier
- `FeatherScatterSpins` — 5-reel, retriggerable free spins
- `CouncilBonusSpins` — 5-reel, progressive multiplier free spins
- `AncestralBonus` — 5-reel, 10-20 free spins, random coin boosts
- `FireCircleBonus` — 5-reel, mystery multiplier free spins
- `TradeRouteBonus` — 5-reel, cascading bonus feature

**Slot Engine C: Cascading/Cluster (3 games)**
- `FeatherCascade` — Vertical cascade, 5 in a row = win
- `RiverStoneCluster` — 5x3 cluster mechanic, expanding wilds
- `GoldRushCascade` — Horizontal cascades, unlimited re-spins

**Slot Engine D: Mega Symbol (3 games)**
- `ColosalEagle` — 4x4 mega eagle, instant 2x payout
- `MegaBuffalo` — 3x3 mega buffalo symbols, wild substitute
- `GoldenCouncil` — 2x2 golden symbols, bonus trigger

**Instant-Win Games (8 games)**
- **Card Reveal**: `LuckyPennyFlip` (pick 5, win all), `FeatherReveal` (9-card grid)
- **Wheel Spin**: `FeatherWheel` (spin for 1-10x multiplier), `SacredSpinner` (bonus wheel)
- **Match**: `FeatherMatch` (match 3 of 5), `RiverMatch` (animated stone match)
- **Dice**: `CouncilDice` (roll 3 dice, sum multiplier), `TradeNumber` (pick 5 numbers)

**Table/Card Games (4 games)**
- **Blackjack**: `FeatherBlackjack` (single hand), `CouncilCards` (multi-hand)
- **Poker**: `SacredPoker` ( 5-card draw), `FeatherHand` (video poker, Jacks or better)

---

#### **B. PARTNER GAMES (20 games — 70/30 split)**

**Partner Studio 1: "Constellation Games"** (8 games)
- `Mystic Fortune` (5-reel wild multiplier)
- `Dragon Dynasty` (5-reel expanding wilds)
- `Phoenix Rising` (5-reel cascade)
- `Celestial Luck` (instant-win card reveal)
- `Starlight Spin` (instant-win wheel)
- `Astral Blackjack` (table: 1/2 hand)
- `Cosmic Poker` (table: video poker)
- `Constellation Match` (instant-win match 3)

**Partner Studio 2: "Sacred Lands"** (7 games)
- `Mountain Peak` (5-reel scatter bonus)
- `Forest Quest` (5-reel free spins)
- `Desert Gold` (5-reel mega symbols)
- `Woodland Luck` (instant-win pick game)
- `Sacred Spin` (instant-win wheel variant)
- `Nature's Hand` (table: poker)
- `Wilderness Roulette` (table: social roulette)

**Partner Studio 3: "Fortune Labs"** (5 games)
- `Golden Age` (5-reel wild multiplier)
- `Lucky Token` (instant-win token match)
- `Fortune Wheel Deluxe` (instant-win enhanced wheel)
- `Jackpot Bluff` (table: poker with raises)
- `Classic Blackjack Pro` (table: multi-hand)

---

### 2.2 Game Mechanics & Compliance

**All games enforce**:
- ✅ No cash references ("earn," "win," "collect" only)
- ✅ No payout promises (language: "potential prize," "if lucky")
- ✅ No "real money" language (use "social coins," "donations")
- ✅ No gambling disclaimers (this isn't gambling legally)
- ✅ All outcomes must be clear (RNG seed logged for disputes)
- ✅ House edge transparent: "Average return 92% (GC), 94% (SC)"

**House Edge Model**:
- **GC games**: 8% average house edge (entertainment)
- **SC games**: 6% average house edge (incentive to donate)
- Difference funds prize pool + nonprofit operations

---

## SECTION 3: REVENUE MODEL

### 3.1 GC Revenue Stream

**Monthly GC Sales (Projection)**:
- $100 avg player × 1,000 active players = $100,000/month

**GC Revenue Distribution**:

```
GC Revenue: $100,000/month
├─ Prize Pool (40%): $40,000
│  └─ Funded prizes, gift cards, PayPal withdrawals
├─ Two Feathers Nationals (50%): $50,000
│  └─ Nonprofit operations, programs, board decisions
├─ Platform Ops (10%): $10,000
│  └─ Server costs, payment processing, support staff
```

**Explanation**:
- Prize pool is NOT "money lost to players" — it's GC that users won
- Charity gets largest cut because this is the core mission
- Ops costs are minimal (headless architecture on Vultr)

---

### 3.2 Partner Revenue Stream

**Partner Game Sales** (estimated 30% of total GC volume from partner games):
- $100,000 total GC × 30% = $30,000 partner game revenue/month

**Partner Split**:
```
Partner Game Revenue: $30,000/month
├─ Partner Studio: $9,000 (30%)
└─ Two Feathers Nationals: $21,000 (70%)
```

**Total charity revenue from GC**: $50,000 (direct) + $21,000 (partner) = **$71,000/month**

---

### 3.3 Donation & SC Revenue

**Donation Processing**:
- Average donation: $25 USD
- Platform fee: 2.2% + $0.30 (via Stripe)
- Nonprofit receives: $24.46 per $25 donation

**SC as Engagement Driver**:
- $25 donation → 25,000 SC
- Player plays more (SC has longer engagement tail than GC)
- Player wins more SC → redeems prizes → more platform engagement
- More engagement → higher LTV → more GC purchases

**Projected Donation Volume**:
- 10% of active players donate monthly
- 1,000 players × 10% = 100 donations/month
- 100 × $25 avg = $2,500/month gross
- 100 × $24.46 net = $2,446/month to nonprofit

**Total monthly charity revenue**:
- GC-based: $71,000
- Donations: $2,446
- **Total: $73,446/month**

---

## SECTION 4: LEGAL COMPLIANCE FRAMEWORK

### 4.1 Why This Is NOT Gambling

**Definition of Gambling**: Exchange real money for a chance to win based on chance or skill, where outcome is random and result is uncertain.

**How RFD Avoids Gambling Classification**:

| Element | Traditional Gambling | RFD Model |
|---------|---|---|
| **Payment** | Wager (money at risk) | Donation (gift, no risk) |
| **Play** | Using wagered money | Using free gifted currency |
| **Outcome** | Win = cash payout | Win = prize from separate pool |
| **Consideration** | Player pays to play | No payment for play |
| **Real Value** | Entire bet at risk | SC is free, no real value risked |

**Legal Theory**: This is a **sweepstakes**, not gambling:
- Entry is free (SC is a gift)
- Outcome is random (RNG-based)
- Prizes are real (funded separately)
- No consideration of payment for entry

**Key Regulatory Quote** (FTC):
> "Sweepstakes require no consideration for entry and random chance determines winners."

---

### 4.2 Firewall Requirements

**Charitable Donation System**:
- ✅ Separate legal entity: Two Feathers Nationals (nonprofit)
- ✅ Separate bank account (no commingling)
- ✅ Donation processor: Stripe Nonprofit or PayPal Giving Fund
- ✅ Tax receipts issued by nonprofit, not platform
- ✅ Annual 990-N filing (nonprofit transparency)

**Game System**:
- ✅ Platform (Two Feather Games LLC) separate from nonprofit
- ✅ No donation language inside games
- ✅ No game outcomes tied to donation matching
- ✅ Prize pool funded from GC revenue (traceable ledger)

**Prize System**:
- ✅ Prize payouts from dedicated fund, not player deposits
- ✅ 1099 issued for prizes >$600/year
- ✅ Prize policy published (RTG — Return to Player)
- ✅ Appeals process for disputed outcomes

---

### 4.3 State-by-State Considerations

**Most US States**: Social gaming is legal (subject to state definitions)

**Problem States**:
- **Washington**: Social gaming with prizes may require license
- **Illinois**: Prize redemptions may need approval
- **New York**: Skill-based game licensing possible

**Strategy**: 
- Launch as "invite-only private beta" in all states
- Obtain legal review in target states before public launch
- Implement geofencing for restricted states
- Have 501(c)(3) approval letter from IRS as defense

---

## SECTION 5: IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Weeks 1-4)
- [ ] Build core slot engine framework (reusable codebase)
- [ ] Implement RNG + fairness auditing
- [ ] Create Stripe + Plaid integration for GC purchases
- [ ] Build SC wallet system (blockchain OR traditional ledger)
- [ ] Create user authentication + KYC for >$600 prizes

**Deliverables**:
- Working slot engine running locally
- Payment processor integration
- User account system with wallet display

---

### Phase 2: Proprietary Games (Weeks 5-8)
- [ ] Deploy 18 proprietary slot games
- [ ] Deploy 8 instant-win games
- [ ] Deploy 4 table/card games
- [ ] Create game library UI (category filters, search)
- [ ] Implement prize redemption system

**Deliverables**:
- 30 playable games in private beta
- Prize redemption workflow end-to-end
- Admin dashboard for game management

---

### Phase 3: Charity Integration (Weeks 9-10)
- [ ] Set up Two Feathers Nationals nonprofit entity (Inc + EIN)
- [ ] Open nonprofit bank account
- [ ] Integrate donation processor (Stripe Nonprofit)
- [ ] Build donation UI + SC gifting automation
- [ ] Create Impact Center (nonprofit mission display)

**Deliverables**:
- Donation button working
- Automatic SC credit upon donation
- Nonprofit transparency page

---

### Phase 4: Partner Onboarding (Weeks 11-14)
- [ ] Create partner portal (game submission + rev-share tracking)
- [ ] Integrate first partner studio (8 games)
- [ ] Implement 70/30 revenue settlement + reporting
- [ ] Build partner compliance checklist + audit trail
- [ ] Deploy second and third partners

**Deliverables**:
- 20 partner games live
- Revenue split tracking
- Partner dashboard (their revenue visibility)

---

### Phase 5: Launch & Scale (Weeks 15-16)
- [ ] Full compliance audit (legal review)
- [ ] Load testing (1,000+ concurrent players)
- [ ] Public beta launch (invite-only)
- [ ] Community building + social features
- [ ] Analytics + engagement optimization

**Deliverables**:
- Live public beta
- 50 games fully operational
- Revenue settlement system running

---

## SECTION 6: COMPETITIVE DIFFERENTIATION

| Aspect | High5 Casino | Crown Coin | **Two Feather Games** |
|--------|---|---|---|
| **Games** | 100+ (generic) | 80+ (generic) | 50 (curated, cultural) |
| **Currency Model** | VIP tier (whales) | Whale focus | 3-tier (GC/SC/Prizes) |
| **Charity** | None | None | 60%+ revenue |
| **Prize Model** | No real prizes | Limited | Real USD/gift cards |
| **Donation Incentive** | None | None | Free SC + tax deduction |
| **Transparency** | Opaque | Opaque | Full audit trail |
| **Cultural Identity** | None | None | Indigenous-rooted |

---

## SECTION 7: RISK MITIGATION

### Legal Risks

**Risk**: State considers SC play "gambling"
**Mitigation**: 
- Keep donation separate from play (different screens)
- Use language: "You received free gift currency, not purchased it"
- Have nonprofit issue receipts, not platform
- Obtain legal opinion in target states

**Risk**: IRS challenges 501(c)(3) nonprofit status
**Mitigation**:
- 990-N filing annual (transparency)
- No excessive compensation to board
- Charity does actual community work (fund programs)
- Keep nonprofit separate from gaming LLC

---

### Financial Risks

**Risk**: Prize payouts exceed GC revenue
**Mitigation**:
- Set house edge conservatively (8-10%)
- Monitor RTG (Return to Player) monthly
- Cap daily prize redemptions if needed
- Maintain 3-month reserve fund

**Risk**: Players abuse referral loops (donate, get SC, cash out)
**Mitigation**:
- Verify donation is real (Stripe confirmed)
- Cap SC earnings per player per month
- Implement play-through requirement (SC must be used 2x before withdrawal)
- Monitor for anomalies

---

### Operational Risks

**Risk**: Partner games contain non-compliant language
**Mitigation**:
- Mandatory compliance review before launch
- Weekly code audit of partner games
- Automatic de-listing if violations found
- Clear contract: "Partner liable for compliance violations"

---

## SECTION 8: NEXT ACTIONS

**Immediate** (This Week):
- [ ] Consult gaming attorney re: sweepstakes vs gambling classification
- [ ] File nonprofit articles of incorporation for Two Feathers Nationals
- [ ] Set up Stripe Nonprofit account for donation processing
- [ ] Create detailed game specification for Slot Engine A

**Short-term** (Next 2 weeks):
- [ ] Build core slot engine framework (code)
- [ ] Create user authentication system
- [ ] Integrate Stripe for GC purchases
- [ ] Begin development on 6 Slot Engine A games

**Medium-term** (Weeks 3-4):
- [ ] Integrate donation processor
- [ ] Build SC wallet system
- [ ] Create prize redemption workflow
- [ ] Deploy first 6 games to private beta

---

## APPENDIX: Currency Conversion Chart

```
Real Money → GC (No Prize Conversion)
$4.99 → 5,000 GC (no withdrawal value)
$9.99 → 10,500 GC (no withdrawal value)
$24.99 → 27,500 GC (no withdrawal value)
$49.99 → 55,000 GC (no withdrawal value)
$99.99 → 110,000 GC (no withdrawal value)

Real Money → SC (Prize Conversion Allowed)
$10 Donation → 10,000 SC (withdraw as prizes at 1:1 ratio)
$25 Donation → 25,000 SC (withdraw as prizes at 1:1 ratio)
$50 Donation → 50,000 SC (withdraw as prizes at 1:1 ratio)
$100 Donation → 100,000 SC (withdraw as prizes at 1:1 ratio)

SC Winnings → Prizes (Real USD)
1,000 SC win → $5 Starbucks card / PayPal
5,000 SC win → $25 Amazon card / PayPal
10,000 SC win → $50 PrepaidCard / PayPal
50,000 SC win → $250 PayPal (requires ID verification)
```

---

**This model is sustainable, legal, and charity-centric. Let's build it.**
