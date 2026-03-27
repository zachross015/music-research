# 03-09-2026

Modifiers to current app:
- Exercise builder? Or at least exercise catalogue with descriptions, visuals, and modifier ideas (eg swing it)

# 03-10-2026

Demonstrate the behavior you want your students to show (responsiveness

New integrations:
- Stretching/yoga every morning right after waking up
- post run stretching 
- Sunday stability sessions
Really need to prioritize these. Starting to notice a lot of bodily tensions and pains. Especially on run today, knee pains were bad.

Should also come up with a set of rules for titles that are hooking but not click bait.

Found myself actually talking about the joy of music with eye doctor. How awesome! Not only did I talk about it, but most of what I talked about was how great it felt to help others with it. To change and heal people with it. So fucking awesome, things are changing from the core! Minor insecurity but I didn't let it stop me. Even asked about her kids and had a discussion about tech

It's interesting today noticing the interactions with Mimza. She's single now, and I'm attracted to her. Don't necessarily want to date her. But what I noticed is that my tendency is to wait for her moves. Embrace her touching me, act playful in response to her. Rarely if ever am I the one making moves. Almost like, to be purely observant, I'm not doing anything. Then hyper fixating on the way she behaves around others vs around me. Looking for signs instead of either trusting instincts or going after what I want. Why?

# 03-11-2026

Rhythm helper app: music theory app which is more rhythm driven. Exercises include:
- Rhythmic dictation
- Rhythm recall
- Tempo identification
- Tempo recall
- Rushing/Dragging recognition

I wonder what the nightmares from the past two nights (Amy and Jess, along with conflict around being bullied) are coming from.
- General unresolved conflicts that, if I were on a show like Alone, would break me over time
- Watching Mimza's breakup
- Seeing how I respond to attraction by defending myself or withdrawing for attention 
- Growing confidence giving me strength to face the discomforts that would have helped me in these scenarios
- Some holding onto them (been thinking about Jess a lot recently)
- Moving towards relationships again making me have to deal with these
- New ways of understanding relationship conflicts and accepting people for who they are, seeing their flaws as a practice of self acceptance

Don't just limit to drums -- build the app (with Claude) to cover ALL aural skills:
- Rhythm skills and dictation
- Music theory
- Tools for EQ, compression, decibel differences

- Levels and experience should still be on a per subject basis
- the CSS on the exercise page is all messed up now
- The unlocks in the leveling should also be on an exponential decay where most unlocks occur towards the beginning and gradually decline over the later levels
- the header on this page looks like it’s supposed to have more but doesn’t

For the visual update:
- I’d like it if key signatures could display the treble and bass clef images of them, and for modes it would be great if each mode had flats and sharps relative to the Ionian mode on sheet paper

For something else:
- There should also be a pitch identifier mode that asks you to identify the played pitch, a similar mode which asks you to identify how many cents off from the “real” pitch the note is, and if at all possible a mode that has you guess (on a slider) how far off a note is being rushed or dragged against a consistent tempo. The last two should be similar to the tempo mode in the way they’re scored.

# 03-12-2026

GOING ABOUT IT ALL WRONG. Or like...this is a good method for right now because it's distinct. BUT THE METHOD WE NEED TO DO IS LIKE DUOLINGO: don't distinguish between listening, sight-singing, piano/sheet music recognition. Instead COMBINE them. Learning intervals should mean learning EVERYTHING with them. One exercise is recognizing perfect 5th or octave, the next is singing it, the next is guessing where on the staff it goes, the next is reading it, etc. cycle that with different intervals until it's ingrained. Then the same with chords, modes, etc. such a good idea. Worth playing with both versions, but it'll be much better if I can gamify it more and more

import { useState, useEffect, useCallback, useRef } from 'react';

const NOTES=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'];
const toDay=()=>new Date().toISOString().split('T')[0];
const MAX_ATT=25;
const MAX_LV=100;

const S={
  async get(k,sh=false){try{const r=await window.storage.get(k,sh);return r?JSON.parse(r.value):null}catch{return null}},
  async set(k,v,sh=false){try{await window.storage.set(k,JSON.stringify(v),sh)}catch{}},
};
const EMPTY_XPM=()=>({intervals:0,chords:0,scales:0,progressions:0,tempo:0});
async function loadProfile(){
  let p=await S.get('rt3:profile');
  if(!p)p={id:Math.random().toString(36).slice(2,9),name:null,xpByMode:EMPTY_XPM(),streak:0,welcomed:false,seenModes:{}};
  // migrate old etXp to xpByMode.intervals
  if(!p.xpByMode){p.xpByMode={...EMPTY_XPM(),intervals:p.etXp||0};delete p.etXp;}
  p.streak=p.streak||0; p.seenModes=p.seenModes||{};
  if(p.welcomed===undefined)p.welcomed=false;
  await S.set('rt3:profile',p); return p;
}
async function saveProfile(p){await S.set('rt3:profile',p);}
async function loadHistory(uid){try{return(await S.get('rt3:hist:'+uid))||[]}catch{return[];}}
async function saveHistory(uid,entry){try{const h=(await S.get('rt3:hist:'+uid))||[];const i=h.findIndex(e=>e.date===entry.date);i>=0?(h[i].total=Math.max(h[i].total,entry.total)):h.push(entry);await S.set('rt3:hist:'+uid,h.slice(-60));}catch{}}
async function loadLB(){try{return(await S.get('rt3:lb:'+toDay(),true))||[]}catch{return[];}}
async function submitLB(p,total){if(!p?.name)return;try{const b=(await S.get('rt3:lb:'+toDay(),true))||[];const i=b.findIndex(e=>e.id===p.id);const e={id:p.id,name:p.name,total,ts:Date.now()};i>=0?b[i]=e:b.push(e);b.sort((a,b)=>b.total-a.total);await S.set('rt3:lb:'+toDay(),b.slice(0,100),true);}catch{}}
async function loadDailyAttempts(){try{return(await S.get('rt3:da:'+toDay()))||{intervals:0,chords:0,scales:0,progressions:0,tempo:0}}catch{return{intervals:0,chords:0,scales:0,progressions:0,tempo:0};}}
async function saveDailyAttempts(d){await S.set('rt3:da:'+toDay(),d);}
async function loadDailyScore(){try{const v=await S.get('rt3:ds:'+toDay());return v||0}catch{return 0;}}
async function saveDailyScore(s){await S.set('rt3:ds:'+toDay(),s);}

// gap(n) = 40+8*(n-1): L1→2=40, L5→6=72, L10→11=112, L20→21=192
function xpForLevel(n){if(n<=1)return 0;let t=0;for(let i=1;i<n;i++)t+=40+8*(i-1);return t;}
function levelFromXp(xp){let n=1;while(n<MAX_LV&&xpForLevel(n+1)<=(xp||0))n++;return n;}
function xpToNext(xp){const lv=levelFromXp(xp);if(lv>=MAX_LV)return{pct:100,need:0,cur:0,lv:MAX_LV};
  const need=40+8*(lv-1);const cur=(xp||0)-xpForLevel(lv);return{pct:Math.min(100,Math.round(cur/need*100)),need,cur,lv};}
function calcXp(streak){return 10+Math.min(streak,20);}
function calcTempoXp(streak,acc){return Math.max(2,Math.round(calcXp(streak)*Math.exp(-3*acc)));}

const KEY_STAGES=[[0],[0,7,5],[0,7,5,2,10],[0,7,5,2,10,9,3],[0,7,5,2,10,9,3,4,8],[0,7,5,2,10,9,3,4,8,11,1],[0,1,2,3,4,5,6,7,8,9,10,11]];
const KEY_INFO={0:{name:'C Major',acc:0,notes:[]},7:{name:'G Major',acc:1,notes:['F#']},5:{name:'F Major',acc:-1,notes:['Bb']},2:{name:'D Major',acc:2,notes:['F#','C#']},10:{name:'Bb Major',acc:-2,notes:['Bb','Eb']},9:{name:'A Major',acc:3,notes:['F#','C#','G#']},3:{name:'Eb Major',acc:-3,notes:['Bb','Eb','Ab']},4:{name:'E Major',acc:4,notes:['F#','C#','G#','D#']},8:{name:'Ab Major',acc:-4,notes:['Bb','Eb','Ab','Db']},11:{name:'B Major',acc:5,notes:['F#','C#','G#','D#','A#']},1:{name:'Db Major',acc:-5,notes:['Bb','Eb','Ab','Db','Gb']},6:{name:'F#/Gb',acc:6,notes:['F#','C#','G#','D#','A#','E#']}};

// Linear unlock design: all core content by Lv 15, keys + advanced drip to Lv 90, nothing after 90.
// Unlock gates: Scales open at Intervals Lv 10 | Chords at Intervals Lv 20 | Progressions at Chords Lv 10
const UNLOCKS_BY_MODE={
  intervals:[
    // ── Core: all 12 intervals by Lv 8, descending at Lv 5 ──
    {lv:1, add:[7,12],  choices:2, tier:2, name:'Perfect 5th & Octave',   desc:'Your first two landmarks — pure power and perfect unity.',          tutKey:'multi-iv-7-12'},
    {lv:2, add:[5],     choices:3, tier:2, name:'Perfect 4th',            desc:'Open and lifting — the foundation of melodic movement.',            tutKey:'iv-5'},
    {lv:3, add:[3,4],   choices:3, tier:2, name:'Minor & Major 3rds',     desc:'The emotional heart of harmony — dark versus bright.',              tutKey:'multi-iv-3-4'},
    {lv:4, add:[9],     choices:4, tier:2, name:'Major 6th',              desc:'Warm and lyrical — jazz gravitates toward this one.',               tutKey:'iv-9'},
    {lv:5, add:[2,10],  choices:4, tier:2, name:'Major 2nd & Minor 7th',  desc:'Stepwise motion and dominant tension — the direction unlocks here.',tutKey:'multi-iv-2-10'},
    {lv:5, type:'direction',       tier:1, name:'Descending Unlocked',    desc:'Intervals now play in both directions. Double the ear training.',   tutKey:'feature-descending'},
    {lv:6, add:[8],     choices:4, tier:2, name:'Minor 6th',              desc:'Tender and bittersweet — the intimate interval.',                   tutKey:'iv-8'},
    {lv:7, add:[1,11],  choices:5, tier:2, name:'Minor 2nd & Major 7th',  desc:'The extremes — sharpest dissonance and luminous near-resolution.',  tutKey:'multi-iv-1-11'},
    {lv:8, add:[6],     choices:5, tier:2, name:'Tritone',                desc:'All 12 intervals now active. Maximum tension — the devil interval.',tutKey:'iv-6'},
    // ── Keys: G/F at 20 (when chords gate opens), then every 15 levels ──
    {lv:20, type:'ivKeys',stage:1, tier:1, name:'G & F Keys',             desc:'One sharp, one flat — your first key signatures.',                  tutKey:'key-stage-1'},
    {lv:30, type:'ivKeys',stage:2, tier:1, name:'D & Bb Keys',            desc:'Two sharps and two flats expand the landscape.',                    tutKey:'key-stage-2'},
    {lv:40, type:'ivKeys',stage:3, tier:1, name:'A & Eb Keys',            desc:'Three sharps and flats — deeper into the circle.',                  tutKey:'key-stage-3'},
    {lv:50, type:'ivKeys',stage:4, tier:1, name:'E & Ab Keys',            desc:'Four sharps and flats — the far reaches.',                          tutKey:'key-stage-4'},
    // ── Compound intervals: spaced evenly from 55–85 ──
    {lv:55, add:[13,14],choices:6, tier:2, name:'9ths',                   desc:'The minor and major 2nds stretched an octave — open and expansive.',tutKey:'iv-13'},
    {lv:60, type:'ivKeys',stage:5, tier:1, name:'B & Db Keys',            desc:'Five sharps and five flats — almost all the way around.',           tutKey:'key-stage-5'},
    {lv:65, add:[15,16],choices:6, tier:2, name:'10ths',                  desc:'3rds across an octave — familiar colours, vast new depth.',          tutKey:'multi-iv-15-16'},
    {lv:72, add:[17,18],choices:6, tier:2, name:'11ths',                  desc:'The 4th and Lydian 4th stretched an octave — wide and airy.',       tutKey:'multi-iv-17-18'},
    {lv:78, add:[19],   choices:6, tier:2, name:'Perfect 12th',           desc:'A 5th across an octave — pure power across a vast range.',          tutKey:'iv-19'},
    {lv:84, add:[20,21],choices:6, tier:2, name:'13ths',                  desc:'Minor and Major 13th — the richest jazz extensions.',               tutKey:'multi-iv-20-21'},
    {lv:88, add:[24],   choices:6, tier:2, name:'Two Octaves',            desc:'The full double span — the complete horizon of your ear.',           tutKey:'iv-24'},
    {lv:90, type:'ivKeys',stage:6, tier:1, name:'All Keys — Intervals',   desc:'Every key, every interval. The full chromatic map is yours.',        tutKey:'key-stage-6'},
  ],
  chords:[
    // ── Core: all 11 basic qualities by Lv 13, keys drip from Lv 20 ──
    {lv:1,  add:['maj','min'],    choices:2, tier:4, name:'Chords Unlocked',        desc:'Major and Minor — the two poles of harmonic colour.',              tutKey:'mode-chords'},
    {lv:2,  add:['dom7'],         choices:3, tier:2, name:'Dominant 7th',           desc:'The jazz workhorse — irresistible pull toward resolution.',         tutKey:'ch-dom7'},
    {lv:3,  add:['maj7'],         choices:3, tier:2, name:'Major 7th',              desc:'Lush and dreamy — the sound of jazz ballads.',                     tutKey:'ch-maj7'},
    {lv:4,  add:['min7'],         choices:4, tier:2, name:'Minor 7th',              desc:'Cool and mellow — the essential jazz minor colour.',               tutKey:'ch-min7'},
    {lv:6,  add:['dim','aug'],    choices:4, tier:2, name:'Dim & Augmented',        desc:'Unstable and mysterious — the extremes of symmetry.',              tutKey:'ch-dim'},
    {lv:9,  add:['hdim7','dim7'], choices:5, tier:2, name:'Half-Dim & Dim 7',       desc:'Sophisticated dark corners — the jazz moody chords.',              tutKey:'ch-hdim7'},
    {lv:13, add:['sus2','sus4'],  choices:5, tier:2, name:'Suspended Chords',       desc:'Ambiguous and floating — all 11 core qualities now in your ear.',  tutKey:'ch-sus2'},
    // ── Keys: start Lv 20, every 15 levels ──
    {lv:20, type:'chKeys',stage:1,tier:1,            name:'G & F Keys',             desc:'First key signatures enter chord training.',                       tutKey:'key-stage-1'},
    {lv:35, type:'chKeys',stage:2,tier:1,            name:'D & Bb Keys',            desc:'Two sharps and two flats for chords.',                            tutKey:'key-stage-2'},
    {lv:50, type:'chKeys',stage:3,tier:1,            name:'A & Eb Keys',            desc:'Three sharps and flats — the harmonic palette expands.',           tutKey:'key-stage-3'},
    {lv:65, type:'chKeys',stage:4,tier:1,            name:'E & Ab Keys',            desc:'Four sharps and flats for chord training.',                        tutKey:'key-stage-4'},
    // ── Advanced: 9th chords and final keys ──
    {lv:75, add:['min9','maj9'],  choices:6, tier:2, name:'9th Chords',             desc:'The full jazz extension — rich, luminous, and complete.',           tutKey:'ch-min9'},
    {lv:80, type:'chKeys',stage:5,tier:1,            name:'B & Db Keys',            desc:'Five sharps and flats for chords.',                               tutKey:'key-stage-5'},
    {lv:90, type:'chKeys',stage:6,tier:1,            name:'All Keys — Chords',      desc:'Every key now active. Every chord quality in every key.',           tutKey:'key-stage-6'},
  ],
  scales:[
    // ── Core: all 13 scale types by Lv 13, descending at Lv 5, keys drip from Lv 22 ──
    {lv:1,  add:['major','natMin'],    choices:2, tier:4, name:'Scales Unlocked',        desc:'Major and Natural Minor — the two poles of tonal colour.',         tutKey:'mode-scales'},
    {lv:2,  add:['majPent','minPent'], choices:3, tier:2, name:'Pentatonic Scales',       desc:'Five notes, zero tension — universally singable.',                 tutKey:'sc-majPent'},
    {lv:3,  add:['blues'],            choices:3, tier:2, name:'Blues Scale',             desc:'Minor pentatonic plus the blue note — raw emotional truth.',       tutKey:'sc-blues'},
    {lv:4,  add:['dorian','mixolyd'], choices:4, tier:2, name:'Dorian & Mixolydian',     desc:'The essential jazz modes — minor with soul, major with edge.',     tutKey:'sc-dorian'},
    {lv:5,  type:'scaleDir',          tier:1,            name:'Descending Scales',       desc:'Scale direction now randomises — ascending and descending.',       tutKey:'feature-descending'},
    {lv:7,  add:['harmMin','melMin'], choices:5, tier:2, name:'Harmonic & Melodic Minor', desc:'Classical tension meets jazz smoothness — raised 7th and 6th.',   tutKey:'sc-harmMin'},
    {lv:10, add:['lydian','phrygian'],choices:5, tier:2, name:'Lydian & Phrygian',       desc:'Dreamy raised 4th and moody flat 2nd — the outer modes.',         tutKey:'sc-lydian'},
    {lv:13, add:['locrian','wholeTone'],choices:6,tier:2, name:'Exotic Scales',          desc:'Locrian and Whole Tone — all 13 scale types now in your ear.',    tutKey:'sc-locrian'},
    // ── Keys: start Lv 22, every ~13 levels ──
    {lv:22, type:'scKeys',stage:1,    tier:1,            name:'G & F Keys',             desc:'First key signatures for scale training.',                         tutKey:'key-stage-1'},
    {lv:35, type:'scKeys',stage:2,    tier:1,            name:'D & Bb Keys',            desc:'Two sharps and two flats for scales.',                             tutKey:'key-stage-2'},
    {lv:48, type:'scKeys',stage:3,    tier:1,            name:'A & Eb Keys',            desc:'Three sharps and flats — the modal palette deepens.',              tutKey:'key-stage-3'},
    {lv:62, type:'scKeys',stage:4,    tier:1,            name:'E & Ab Keys',            desc:'Four sharps and flats for scale training.',                        tutKey:'key-stage-4'},
    {lv:76, type:'scKeys',stage:5,    tier:1,            name:'B & Db Keys',            desc:'Five sharps and flats — nearly all the way around.',               tutKey:'key-stage-5'},
    {lv:90, type:'scKeys',stage:6,    tier:1,            name:'All Keys — Scales',      desc:'Every key now active. Every scale in every key.',                  tutKey:'key-stage-6'},
  ],
  progressions:[
    // ── Core: all 8 progressions by Lv 14, keys drip from Lv 22 ──
    {lv:1,  add:['I_IV_V_I','I_vi_IV_V'],  choices:2, tier:4, name:'Progressions Unlocked', desc:'The foundation of Western harmony and the timeless 50s cycle.',  tutKey:'mode-progressions'},
    {lv:2,  add:['I_V_vi_IV'],             choices:3, tier:2, name:'I-V-vi-IV',             desc:'The axis progression — the backbone of modern song-writing.',    tutKey:'pg-I_V_vi_IV'},
    {lv:4,  add:['ii_V_I'],               choices:3, pgKeys:1,tier:2, name:'ii-V-I',        desc:'The DNA of bebop — the most important cadence in all of jazz.',  tutKey:'pg-ii_V_I'},
    {lv:7,  add:['iii_VI_ii_V'],          choices:4, pgKeys:2,tier:2, name:'Jazz Turnaround',desc:'The cycle-of-5ths turnaround — the jazz heartbeat.',            tutKey:'pg-iii_VI_ii_V'},
    {lv:10, add:['i_iv_V','blues'],        choices:4, pgKeys:3,tier:2, name:'Minor & Blues', desc:'Raw emotion and 12-bar soul.',                                  tutKey:'pg-blues'},
    {lv:14, add:['tritone'],              choices:5, pgKeys:4,tier:2, name:'Tritone Sub',    desc:'All 8 progressions active. The art of reharmonisation.',         tutKey:'pg-tritone'},
    // ── Keys: start Lv 22, every ~17 levels ──
    {lv:22, type:'pgKeys',stage:1,         tier:1,            name:'G & F Keys',            desc:'First key signatures for progression training.',                  tutKey:'key-stage-1'},
    {lv:38, type:'pgKeys',stage:2,         tier:1,            name:'D & Bb Keys',           desc:'Two sharps and two flats for progressions.',                      tutKey:'key-stage-2'},
    {lv:54, type:'pgKeys',stage:3,         tier:1,            name:'A & Eb Keys',           desc:'Three sharps and flats — the harmonic world expands.',            tutKey:'key-stage-3'},
    {lv:68, type:'pgKeys',stage:4,         tier:1,            name:'E & Ab Keys',           desc:'Four sharps and flats for progression training.',                 tutKey:'key-stage-4'},
    {lv:80, type:'pgKeys',stage:5,         tier:1,            name:'B & Db Keys',           desc:'Five sharps and flats — nearly every key covered.',               tutKey:'key-stage-5'},
    {lv:90, type:'pgKeys',stage:6,         tier:1,            name:'All Keys — Progressions',desc:'Every key now active. Every progression in every key.',          tutKey:'key-stage-6'},
  ],
  tempo:[
    {lv:1,  tier:4, name:'Tempo Unlocked',    desc:'The pulse is the foundation of everything. Feel the beat.',    tutKey:'mode-tempo'},
    {lv:5,  tier:1, name:'Wider BPM Range',   desc:'More tempos now included — from slow to brisk.',               tutKey:'mode-tempo'},
    {lv:15, tier:1, name:'Full BPM Range',    desc:'The full range of musical tempos is now in play.',             tutKey:'mode-tempo'},
    {lv:90, tier:2, name:'Tempo — Complete',  desc:'Your internal metronome is calibrated across every speed.',    tutKey:'mode-tempo'},
  ],
};

function getModeConfig(mode, lv){
  const c={pool:[],choices:2,keyStage:0,dirOn:false};
  for(const u of (UNLOCKS_BY_MODE[mode]||[])){
    if(u.lv>lv)break;
    if(u.add)c.pool.push(...u.add);
    if(u.choices)c.choices=u.choices;
    if(u.type==='ivKeys'||u.type==='chKeys'||u.type==='scKeys'||u.type==='pgKeys')c.keyStage=u.stage;
    if(u.pgKeys!==undefined)c.keyStage=u.pgKeys;
    if(u.type==='direction'||u.type==='scaleDir')c.dirOn=true;
  }
  return c;
}
function getContent(xpByMode){
  const xm=xpByMode||EMPTY_XPM();
  const ivLv=levelFromXp(xm.intervals);
  const chLv=levelFromXp(xm.chords);
  const scLv=levelFromXp(xm.scales);
  const pgLv=levelFromXp(xm.progressions);
  const tpLv=levelFromXp(xm.tempo);
  const iv=getModeConfig('intervals',ivLv);
  const ch=getModeConfig('chords',chLv);
  const sc=getModeConfig('scales',scLv);
  const pg=getModeConfig('progressions',pgLv);
  return{
    intervals:{...iv,on:true},
    chords:{...ch,on:ivLv>=20&&ch.pool.length>0},
    scales:{...sc,on:ivLv>=10&&sc.pool.length>0},
    progressions:{...pg,on:chLv>=10&&pg.pool.length>0},
    tempo:{pool:[],choices:0,keyStage:0,dirOn:false,on:ivLv>=8},
    dirOn:iv.dirOn, scaleDirOn:sc.dirOn,
    modeLevels:{intervals:ivLv,chords:chLv,scales:scLv,progressions:pgLv,tempo:tpLv},
  };
}

const IV=[
  {id:1, abbr:'m2', name:'Minor 2nd',    q:'Half step — sharp, biting dissonance.',         ref:'Jaws theme'},
  {id:2, abbr:'M2', name:'Major 2nd',    q:'Whole step — smooth, stepwise motion.',          ref:'Happy Birthday (first two notes)'},
  {id:3, abbr:'m3', name:'Minor 3rd',    q:'Dark and introspective — the blues third.',      ref:'Smoke on the Water'},
  {id:4, abbr:'M3', name:'Major 3rd',    q:'Bright and stable — the sunny third.',           ref:'Oh! Susanna'},
  {id:5, abbr:'P4', name:'Perfect 4th',  q:'Open and strong — foundational movement.',       ref:'Here Comes the Bride'},
  {id:6, abbr:'TT', name:'Tritone',      q:'Maximum tension — the devil interval.',          ref:'The Simpsons theme'},
  {id:7, abbr:'P5', name:'Perfect 5th',  q:'Pure power — the backbone of harmony.',          ref:'Star Wars main theme'},
  {id:8, abbr:'m6', name:'Minor 6th',    q:'Tender and bittersweet.',                        ref:'The Entertainer (opening)'},
  {id:9, abbr:'M6', name:'Major 6th',    q:'Warm and lyrical — jazz loves this one.',        ref:'My Bonnie Lies Over the Ocean'},
  {id:10,abbr:'m7', name:'Minor 7th',    q:'Dominant tension — pull to resolve.',            ref:'Somewhere (West Side Story)'},
  {id:11,abbr:'M7', name:'Major 7th',    q:'Luminous and searching — almost resolved.',      ref:'Take On Me (chorus leap)'},
  {id:12,abbr:'P8', name:'Octave',       q:'Perfect unity — same note, new register.',       ref:'Somewhere Over the Rainbow'},
  {id:13,abbr:'m9', name:'Minor 9th',    q:'Like a minor 2nd — wider and more open.',        ref:'m2 placed over an octave'},
  {id:14,abbr:'M9', name:'Major 9th',    q:'The classic jazz extension — expansive.',         ref:'M2 placed over an octave'},
  {id:15,abbr:'m10',name:'Minor 10th',   q:'A minor 3rd across an octave.',                  ref:'Sweet melancholy with depth'},
  {id:16,abbr:'M10',name:'Major 10th',   q:'A major 3rd with extra warmth.',                 ref:'Bright sunshine, expanded'},
  {id:17,abbr:'P11',name:'Perf 11th',    q:'Like a 4th — open and floating.',                ref:'P4 placed an octave higher'},
  {id:18,abbr:'A11',name:'Aug 11th',     q:'The Lydian sound — bright and elevated.',         ref:'Debussy and film scores'},
  {id:19,abbr:'P12',name:'Perf 12th',    q:'A 5th stretched — pure and resonant.',            ref:'Power and open space'},
  {id:20,abbr:'m13',name:'Minor 13th',   q:'Moody and complex — rich jazz colour.',           ref:'Deep jazz voicings'},
  {id:21,abbr:'M13',name:'Major 13th',   q:'The full jazz extension — bright and complete.',  ref:'Lush jazz chords'},
  {id:24,abbr:'2P8',name:'Two Octaves',  q:'Double the distance — perfectly unified.',        ref:'Outer edge of vocal range'},
];
const CH={
  maj:{id:'maj',  name:'Major',       abbr:'Maj', ivs:[0,4,7],       q:'Bright and stable.',              formula:'Root + M3 + P5'},
  min:{id:'min',  name:'Minor',       abbr:'min', ivs:[0,3,7],       q:'Dark and introspective.',          formula:'Root + m3 + P5'},
  dim:{id:'dim',  name:'Diminished',  abbr:'dim', ivs:[0,3,6],       q:'Tense and unstable.',              formula:'Root + m3 + d5'},
  aug:{id:'aug',  name:'Augmented',   abbr:'aug', ivs:[0,4,8],       q:'Mysterious and unresolved.',       formula:'Root + M3 + A5'},
  dom7:{id:'dom7',name:'Dominant 7',  abbr:'7',   ivs:[0,4,7,10],    q:'Strong pull to resolve.',          formula:'Major + m7'},
  maj7:{id:'maj7',name:'Major 7',     abbr:'Maj7',ivs:[0,4,7,11],    q:'Lush and dreamy.',                 formula:'Major + M7'},
  min7:{id:'min7',name:'Minor 7',     abbr:'m7',  ivs:[0,3,7,10],    q:'Cool and mellow.',                 formula:'Minor + m7'},
  hdim7:{id:'hdim7',name:'Half-Dim 7',abbr:'o7',  ivs:[0,3,6,10],    q:'Moody — ii chord in minor.',       formula:'Dim + m7'},
  dim7:{id:'dim7',name:'Dim 7',       abbr:'d7',  ivs:[0,3,6,9],     q:'Fully symmetric — unstable.',      formula:'Dim + d7'},
  sus2:{id:'sus2',name:'Sus 2',       abbr:'sus2',ivs:[0,2,7],       q:'Open and floating — no third.',    formula:'Root + M2 + P5'},
  sus4:{id:'sus4',name:'Sus 4',       abbr:'sus4',ivs:[0,5,7],       q:'Ambiguous tension.',                formula:'Root + P4 + P5'},
  min9:{id:'min9',name:'Minor 9',     abbr:'m9',  ivs:[0,3,7,10,14], q:'Rich jazz minor colour.',           formula:'m7 chord + M9'},
  maj9:{id:'maj9',name:'Major 9',     abbr:'Maj9',ivs:[0,4,7,11,14], q:'Expansive and luminous.',           formula:'Maj7 chord + M9'},
};
const SC=[
  {id:'major',    name:'Major',            ivs:[0,2,4,5,7,9,11], q:'The universal bright scale.',          steps:'W-W-H-W-W-W-H',  char:'Leading tone (M7) pulls home'},
  {id:'natMin',   name:'Natural Minor',    ivs:[0,2,3,5,7,8,10], q:'Dark and expressive.',                 steps:'W-H-W-W-H-W-W',  char:'Flat 3, 6, 7 give the dark tone'},
  {id:'harmMin',  name:'Harmonic Minor',   ivs:[0,2,3,5,7,8,11], q:'Classical tension.',                   steps:'W-H-W-W-H-A2-H', char:'Raised 7 creates exotic aug 2nd'},
  {id:'melMin',   name:'Melodic Minor',    ivs:[0,2,3,5,7,9,11], q:'Jazz minor — smooth ascending.',       steps:'W-H-W-W-W-W-H',  char:'Raised 6 and 7 smooth the line'},
  {id:'dorian',   name:'Dorian',           ivs:[0,2,3,5,7,9,10], q:'Minor with a raised 6th.',             steps:'W-H-W-W-W-H-W',  char:'Raised 6th is the fingerprint'},
  {id:'phrygian', name:'Phrygian',         ivs:[0,1,3,5,7,8,10], q:'Spanish — flat 2nd rules.',            steps:'H-W-W-W-H-W-W',  char:'Flat 2nd is the Spanish colour'},
  {id:'lydian',   name:'Lydian',           ivs:[0,2,4,6,7,9,11], q:'Raised 4th — dreamy.',                 steps:'W-W-W-H-W-W-H',  char:'Raised 4th is its magic'},
  {id:'mixolyd',  name:'Mixolydian',       ivs:[0,2,4,5,7,9,10], q:'Major with flat 7.',                   steps:'W-W-H-W-W-H-W',  char:'Flat 7 is the blues fingerprint'},
  {id:'locrian',  name:'Locrian',          ivs:[0,1,3,5,6,8,10], q:'Flat 2nd and 5th — most unstable.',    steps:'H-W-W-H-W-W-W',  char:'Dim 5th is most unstable'},
  {id:'majPent',  name:'Major Pentatonic', ivs:[0,2,4,7,9],       q:'Five notes, zero tension.',            steps:'W-W-m3-W-m3',    char:'No semitones — universally singable'},
  {id:'minPent',  name:'Minor Pentatonic', ivs:[0,3,5,7,10],      q:'Rock and blues backbone.',             steps:'m3-W-W-m3-W',    char:'Foundation of rock guitar'},
  {id:'blues',    name:'Blues Scale',      ivs:[0,3,5,6,7,10],    q:'Minor pent plus the blue note.',       steps:'m3-W-H-H-m3-W',  char:'Blue note (b5) is the soul'},
  {id:'wholeTone',name:'Whole Tone',       ivs:[0,2,4,6,8,10],    q:'Symmetric — Debussy-like.',            steps:'W-W-W-W-W-W',    char:'All whole steps — symmetric'},
];
const SC_BY=Object.fromEntries(SC.map(s=>[s.id,s]));
const PG=[
  {id:'I_IV_V_I',    name:'I-IV-V-I',    chs:[{o:0,t:'maj'},{o:5,t:'maj'},{o:7,t:'maj'},{o:0,t:'maj'}],        q:"Western harmony's foundation."},
  {id:'I_vi_IV_V',   name:'I-vi-IV-V',   chs:[{o:0,t:'maj'},{o:9,t:'min'},{o:5,t:'maj'},{o:7,t:'maj'}],        q:'The timeless 50s progression.'},
  {id:'I_V_vi_IV',   name:'I-V-vi-IV',   chs:[{o:0,t:'maj'},{o:7,t:'maj'},{o:9,t:'min'},{o:5,t:'maj'}],        q:'Axis — modern pop DNA.'},
  {id:'ii_V_I',      name:'ii-V-I',      chs:[{o:2,t:'min7'},{o:7,t:'dom7'},{o:0,t:'maj7'}],                    q:'The fundamental jazz cadence.'},
  {id:'iii_VI_ii_V', name:'iii-VI-ii-V', chs:[{o:4,t:'min7'},{o:9,t:'dom7'},{o:2,t:'min7'},{o:7,t:'dom7'}],    q:'Cycle-of-5ths turnaround.'},
  {id:'i_iv_V',      name:'i-iv-V',      chs:[{o:0,t:'min'},{o:5,t:'min'},{o:7,t:'maj'}],                       q:'Minor blues — raw pull.'},
  {id:'blues',       name:'12-bar Blues', chs:[{o:0,t:'dom7'},{o:5,t:'dom7'},{o:0,t:'dom7'},{o:7,t:'dom7'}],    q:'The heartbeat of blues.'},
  {id:'tritone',     name:'ii-bVII-I',   chs:[{o:2,t:'min7'},{o:10,t:'dom7'},{o:0,t:'maj7'}],                   q:'Tritone substitution.'},
];
const PG_BY=Object.fromEntries(PG.map(p=>[p.id,p]));

const EXERCISE_INTROS={
  intervals:{icon:'↔',color:'#9CB7B1',headline:'Interval Training',
    what:'An interval is the distance between two notes, measured in semitones. Every melody, chord, and scale is built from intervals stacked together.',
    how:'You will hear two notes in sequence. Identify the interval between them by selecting from the options. The more you practise, the more each interval develops its own distinct emotional signature.',
    why:'Interval recognition is the foundation of all ear training. It unlocks transcription, improvisation by ear, and instinctive harmonic understanding.',
    example:'The opening two notes of Star Wars form a Perfect 5th. Smoke on the Water opens with a Minor 3rd. Once those signatures lock in, you hear them everywhere.'},
  chords:{icon:'♪',color:'#C6A585',headline:'Chord Recognition',
    what:'A chord is three or more notes sounding together. The quality — major, minor, dominant — determines its emotional colour and harmonic function.',
    how:'You will hear a chord played as an arpeggio. Focus on the overall feeling: bright, dark, tense, floating. That feeling is your guide to the name.',
    why:'Chord recognition lets you analyse songs by ear, communicate with other musicians instantly, and understand the logic beneath any piece of music.',
    example:'Major sounds open and bright. Minor sounds dark and inward. Dominant 7th has a tense, unresolved pull. Those feelings come before the labels.'},
  scales:{icon:'〜',color:'#BEC9A6',headline:'Scale Recognition',
    what:'A scale is a specific sequence of notes following a pattern of whole and half steps. Scales are the horizontal dimension of music — melody lives here.',
    how:'You will hear all the notes of a scale in order. Identify the scale type. Listen for the characteristic tone — the note that makes it feel distinctly like that scale.',
    why:'Scale recognition connects your ear to the modes used across all genres. It unlocks improvisation, composition, and deep melodic understanding.',
    example:'Dorian sounds like natural minor with a raised 6th — that one note gives it a jazz-blues quality. One note changes everything.'},
  progressions:{icon:'♫',color:'#BEC9A6',headline:'Progression Recognition',
    what:'A chord progression is a sequence of chords moving through time. The movement between them — tension, direction, resolution — creates musical narrative.',
    how:'You will hear a series of chords in a key. Identify the progression. Feel the motion — where does it want to go? Stable, questioning, or resolved?',
    why:'Progressions are the sentences of harmonic language. Recognising them lets you learn songs instantly and understand why music feels the way it does.',
    example:'The ii-V-I is the heartbeat of jazz — present in nearly every standard. Once locked in, it is unmistakable.'},
  tempo:{icon:'♩',color:'#D1E1DD',headline:'Tempo Recognition',
    what:'Tempo is the pulse — the steady heartbeat that all music lives inside. Measured in BPM, it is the rhythmic foundation beneath every note.',
    how:'You will hear a series of clicks at a steady tempo. Count the beats and submit your BPM estimate. Feel the space between beats — do not calculate, feel.',
    why:'A strong internal metronome is one of the most underrated musician skills. It lets you lock in with other players and feel rhythm as a physical presence.',
    example:'60 BPM is a slow heartbeat at rest. 120 BPM is a brisk walk. Start by connecting tempo to physical movement.'},
};
const MODE_INTRO={
  chords:{headline:'From Intervals to Chords',icon:'♪',color:'#C6A585',body:'You have been hearing the distance between two notes. Chords are what happens when those distances stack — three or more notes at once. A major chord is a major 3rd plus a perfect 5th. Your ear already knows those intervals.',tips:['Major = Root + M3 + P5','Minor = Root + m3 + P5','One semitone apart — enormous emotional difference']},
  scales:{headline:'From Chords to Scales',icon:'〜',color:'#9CB7B1',body:'Chords grow out of scales. A 7-note scale is a set of notes that feel natural together. Every chord you know is built from alternating notes of a scale. The major scale (W-W-H-W-W-W-H) is where Western harmony begins.',tips:['Scales are the vocabulary; chords are the sentences','Major scale: Whole-Whole-Half-Whole-Whole-Whole-Half','Every scale degree produces a different chord quality']},
  progressions:{headline:'From Scales to Progressions',icon:'♫',color:'#BEC9A6',body:'A progression is music in motion — chords moving in a pattern. Each chord in a scale has a Roman numeral. The ii-V-I is the DNA of bebop. The I-IV-V-I is the heartbeat of the blues.',tips:['Uppercase = major, lowercase = minor','ii-V-I is the most important progression in jazz','Learn to hear it in every key']},
  tempo:{headline:'The Rhythmic Foundation',icon:'♩',color:'#D1E1DD',body:'Every interval, chord, and progression lives inside a rhythmic frame. Tempo is the heartbeat that gives music its sense of time. Training your internal metronome transforms how you play with others.',tips:['Listen for the beat, not just the first click','Count in groups of four','A strong inner pulse means you can play anywhere']},
};

function sf(s){return 261.6256*Math.pow(2,s/12);}
function tone(ctx,freq,t,dur,vol=0.2,type='triangle'){const o=ctx.createOscillator(),g=ctx.createGain();o.connect(g);g.connect(ctx.destination);o.type=type;o.frequency.value=freq;g.gain.setValueAtTime(0,t);g.gain.linearRampToValueAtTime(vol,t+0.03);g.gain.exponentialRampToValueAtTime(0.001,t+dur);o.start(t);o.stop(t+dur);}
function clk(ctx,t,acc){const o=ctx.createOscillator(),g=ctx.createGain();o.connect(g);g.connect(ctx.destination);o.type='sine';o.frequency.value=acc?1100:880;g.gain.setValueAtTime(acc?.35:.2,t);g.gain.exponentialRampToValueAtTime(0.001,t+0.06);o.start(t);o.stop(t+0.1);}
function playOK(ctx){const n=ctx.currentTime;[0,4,7,12].forEach((s,i)=>tone(ctx,sf(s),n+i*.07,.25,.18));}
function playNG(ctx){const n=ctx.currentTime;tone(ctx,sf(-12),n,.45,.28);tone(ctx,sf(-11),n+.03,.4,.18);}
function scheduleAudio(ctx,q){
  const n=ctx.currentTime;const dir=q.dir||'asc';
  if(q.type==='interval'){const[a,b]=dir==='desc'?[q.nb,q.na]:[q.na,q.nb];tone(ctx,sf(a),n,.85);tone(ctx,sf(b),n+.75,.85);return 1700;}
  if(q.type==='chord'){CH[q.cid].ivs.forEach((iv,i)=>tone(ctx,sf(q.root+iv),n+i*.02,1.2));return 1600;}
  if(q.type==='scale'){const notes=[...SC_BY[q.cid].ivs,12];const ord=dir==='desc'?[...notes].reverse():notes;ord.forEach((iv,i)=>tone(ctx,sf(q.root+iv),n+i*.2,.28,.18));return ord.length*200+400;}
  if(q.type==='progression'){let t=n;PG_BY[q.cid].chs.forEach(ch=>{CH[ch.t].ivs.forEach((iv,i)=>tone(ctx,sf(q.root+ch.o+iv),t+i*.02,.9,.16));t+=1.25;});return PG_BY[q.cid].chs.length*1250+400;}
  if(q.type==='tempo'){const bMs=60000/q.cid;for(let i=0;i<q.beats;i++)clk(ctx,n+(i*bMs)/1000,i%4===0);return q.beats*bMs+300;}
  return 1000;
}
function playTutSound(ctx,tutKey){
  const n=ctx.currentTime;
  const im=tutKey?.match(/^(?:multi-)?iv-(.+)$/);if(im){tone(ctx,sf(0),n,.85);tone(ctx,sf(parseInt(im[1])),n+.75,.85);return;}
  const cm=tutKey?.match(/^ch-(.+)$/);if(cm&&CH[cm[1]]){CH[cm[1]].ivs.forEach((iv,i)=>tone(ctx,sf(iv),n+i*.02,1.2));return;}
  const sm=tutKey?.match(/^sc-(.+)$/);if(sm&&SC_BY[sm[1]]){[...SC_BY[sm[1]].ivs,12].forEach((iv,i)=>tone(ctx,sf(iv),n+i*.2,.28,.18));}
}

function initW(pool){const w={};pool.forEach(id=>{w[String(id)]=3;});return w;}
function wPick(pool,w){const tot=pool.reduce((s,id)=>s+(w[String(id)]||1),0);let r=Math.random()*tot;for(const id of pool){r-=(w[String(id)]||1);if(r<=0)return id;}return pool[pool.length-1];}
function wUpd(w,id,ok){const nw={...w},k=String(id);nw[k]=ok?Math.max(.4,(nw[k]||3)*.72):Math.min(9,(nw[k]||3)*1.5);return nw;}
function shuf(arr){const a=[...arr];for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
function confChoices(pool,cid,n,cRow={}){const others=pool.filter(id=>String(id)!==String(cid));const sc=others.map(id=>({id,score:1+(cRow[String(id)]||0)*5}));const sel=[],rem=[...sc];for(let i=0;i<Math.min(n-1,rem.length);i++){const tot=rem.reduce((s,x)=>s+x.score,0);let r=Math.random()*tot;let ix=rem.length-1;for(let j=0;j<rem.length;j++){r-=rem[j].score;if(r<=0){ix=j;break;}}sel.push(rem[ix].id);rem.splice(ix,1);}return shuf([cid,...sel]);}
function buildQ(mode,content,weights,confMatrix){
  const cfg=content[mode];
  const keyPool=KEY_STAGES[cfg?.keyStage||0]||[0];
  const root=keyPool[Math.floor(Math.random()*keyPool.length)];
  const canFlip=cfg?.dirOn||(mode==='scales'&&content.scaleDirOn);
  const dir=canFlip&&Math.random()<.5?'desc':'asc';
  if(mode==='tempo'){
    const tpLv=content.modeLevels?.tempo||1;
    const pool=tpLv>=15?[60,72,80,88,96,104,112,120,132,144,160]:tpLv>=5?[72,88,96,112,120,132,144]:[80,96,112,120];
    return{type:'tempo',cid:pool[Math.floor(Math.random()*pool.length)],beats:8};
  }
  const cid=wPick(cfg.pool,weights[mode]||initW(cfg.pool));
  const cRow=(confMatrix[mode]||{})[String(cid)]||{};
  const choices=confChoices(cfg.pool,cid,cfg.choices,cRow);
  if(mode==='intervals')return{type:'interval',cid,na:root,nb:root+cid,oct:cfg.choices>=6?2:1,choices:choices.map(id=>IV.find(x=>x.id===id)),dir};
  if(mode==='chords')return{type:'chord',cid,root,choices:choices.map(id=>CH[id]),dir:'asc'};
  if(mode==='scales')return{type:'scale',cid,root,choices:choices.map(id=>SC_BY[id]),dir};
  return{type:'progression',cid,root,choices:choices.map(id=>PG_BY[id]),dir:'asc'};
}
function getLabel(q){if(!q)return null;if(q.type==='interval')return IV.find(x=>x.id===q.cid);if(q.type==='chord')return CH[q.cid];if(q.type==='scale')return SC_BY[q.cid];if(q.type==='progression')return PG_BY[q.cid];return{name:q.cid+' BPM',q:'Feel the pulse.'};}

let _ctx=null;function getCtx(){if(!_ctx||_ctx.state==='closed')_ctx=new(window.AudioContext||window.webkitAudioContext)();return _ctx;}

function Piano({na,nb,octs=1}){
  const WW=28,GAP=2,BW=16,BH=54,WH=88,U=WW+GAP;
  const WK=[0,2,4,5,7,9,11],BK=[[1,0],[3,1],[6,3],[8,4],[10,5]];
  const ws=[],bs=[];
  for(let o=0;o<octs;o++){
    WK.forEach((s,wi)=>{const abs=o*12+s;ws.push({abs,x:(o*7+wi)*U,a:abs===na,b:abs===nb});});
    BK.forEach(([s,aw])=>{const abs=o*12+s,x=(o*7+aw+1)*U-BW/2-1;bs.push({abs,x,a:abs===na,b:abs===nb});});
  }
  const tw=octs*7*U-GAP;
  return(<div style={{overflowX:'auto',margin:'2px 0 10px',display:'flex',justifyContent:'center'}}>
    <svg width={Math.min(tw,370)} height={WH} viewBox={'0 0 '+tw+' '+WH} style={{display:'block'}}>
      {ws.map(k=><rect key={k.abs} x={k.x} y={0} width={WW} height={WH} rx={3} fill={k.a?'#D1E1DD':k.b?'rgba(198,165,133,.35)':'white'} stroke={k.a?'#9CB7B1':k.b?'#C6A585':'#BEC9A6'} strokeWidth={1.5}/>)}
      {bs.map(k=><rect key={k.abs} x={k.x} y={0} width={BW} height={BH} rx={2} fill={k.a?'#9CB7B1':k.b?'#C6A585':'#405147'}/>)}
      {ws.filter(k=>k.a||k.b).map(k=><circle key={'d'+k.abs} cx={k.x+WW/2} cy={WH-10} r={4} fill={k.a?'#405147':'#C6A585'}/>)}
      {bs.filter(k=>k.a||k.b).map(k=><circle key={'d'+k.abs} cx={k.x+BW/2} cy={BH-9} r={3} fill='#F2EEE6'/>)}
    </svg></div>);
}
function ScalePiano({root,ivs}){
  const tones=new Set(ivs.map(iv=>(root+iv)%12));
  const WW=24,GAP=2,BW=14,BH=50,WH=80,U=WW+GAP;
  const WK=[0,2,4,5,7,9,11],BK=[[1,0],[3,1],[6,3],[8,4],[10,5]];
  const ws=WK.map((s,wi)=>({s,x:wi*U,on:tones.has(s)}));
  const bs=BK.map(([s,aw])=>({s,x:(aw+1)*U-BW/2-1,on:tones.has(s)}));
  const tw=7*U-GAP;
  return(<svg width={tw} height={WH} viewBox={'0 0 '+tw+' '+WH}>
    {ws.map(k=><rect key={k.s} x={k.x} y={0} width={WW} height={WH} rx={3} fill={k.on?'#D1E1DD':'white'} stroke={k.on?'#9CB7B1':'#BEC9A6'} strokeWidth={1.5}/>)}
    {bs.map(k=><rect key={k.s} x={k.x} y={0} width={BW} height={BH} rx={2} fill={k.on?'#9CB7B1':'#405147'}/>)}
  </svg>);
}

let _tutCtx=null;function getCtxT(){if(!_tutCtx||_tutCtx.state==='closed')_tutCtx=new(window.AudioContext||window.webkitAudioContext)();return _tutCtx;}
function TutorialSheet({tutKey,onClose}){
  const[playing,setPlaying]=useState(false);
  if(!tutKey)return null;
  const ivM=tutKey.match(/^(?:multi-)?iv-(.+)$/);
  const chM=tutKey.match(/^ch-(.+)$/);const scM=tutKey.match(/^sc-(.+)$/);const pgM=tutKey.match(/^pg-(.+)$/);
  const modeM=tutKey.match(/^mode-(.+)$/);const keyM=tutKey.match(/^key-stage-(\d+)$/);
  const iv=ivM?IV.find(x=>x.id===parseInt(ivM[1])):null;
  const ch=chM?CH[chM[1]]:null;const sc=scM?SC_BY[scM[1]]:null;const pg=pgM?PG_BY[pgM[1]]:null;
  const modeData=modeM?MODE_INTRO[modeM[1]]:null;const keyStage=keyM?parseInt(keyM[1]):null;
  const tc=iv?{type:'iv',data:iv}:ch?{type:'ch',data:ch}:sc?{type:'sc',data:sc}:pg?{type:'pg',data:pg}:modeData?{type:'mode',data:modeData}:keyStage!==null?{type:'key',stage:keyStage}:null;
  function doPlay(){if(playing)return;setPlaying(true);try{const ctx=getCtxT();if(ctx.state==='suspended')ctx.resume().then(()=>{playTutSound(ctx,tutKey);setTimeout(()=>setPlaying(false),2000);});else{playTutSound(ctx,tutKey);setTimeout(()=>setPlaying(false),2000);}}catch{setPlaying(false);}}
  return(
    <div style={{position:'fixed',inset:0,background:'rgba(64,81,71,.5)',zIndex:50,display:'flex',alignItems:'flex-end',animation:'ri_fadeIn .2s'}} onClick={e=>e.target===e.currentTarget&&onClose()}>
      <div style={{background:'#F2EEE6',width:'100%',maxWidth:430,margin:'0 auto',borderRadius:'22px 22px 0 0',maxHeight:'88vh',display:'flex',flexDirection:'column',animation:'ri_slideSheet .3s'}}>
        <div style={{width:34,height:4,background:'#BEC9A6',borderRadius:2,margin:'10px auto 0'}}/>
        <div style={{overflowY:'auto',padding:'16px 20px 32px'}}>
          {tc?.type==='iv'&&(<><div style={{fontFamily:"'Fraunces',serif",fontSize:22,fontWeight:700,color:'#405147',marginBottom:4}}>{tc.data.name} <span style={{color:'#9CB7B1',fontSize:14}}>({tc.data.abbr})</span></div>
            <div style={{fontSize:12,color:'#9CB7B1',marginBottom:10}}>{tc.data.id} semitone{tc.data.id!==1?'s':''}</div>
            <Piano na={0} nb={tc.data.id} octs={tc.data.id>12?2:1}/>
            <div style={{background:'white',borderRadius:10,padding:'10px 13px',marginBottom:10,fontSize:12,color:'#405147',lineHeight:1.6}}>{tc.data.q}</div>
            <div style={{fontSize:11,color:'#9CB7B1',marginBottom:12}}>Reference: {tc.data.ref}</div>
            <button onClick={doPlay} disabled={playing} style={{width:'100%',padding:'9px',background:'#405147',color:'#F2EEE6',border:'none',borderRadius:10,fontFamily:"'Work Sans',sans-serif",fontSize:12,fontWeight:600,cursor:playing?'default':'pointer',opacity:playing?.7:1}}>{playing?'Playing…':'▶ Hear It'}</button></>)}
          {tc?.type==='ch'&&(<><div style={{fontFamily:"'Fraunces',serif",fontSize:22,fontWeight:700,color:'#405147',marginBottom:4}}>{tc.data.name}</div>
            <div style={{fontSize:11,color:'#9CB7B1',marginBottom:8}}>{tc.data.formula}</div>
            <ScalePiano root={0} ivs={tc.data.ivs}/>
            <div style={{background:'white',borderRadius:10,padding:'10px 13px',marginBottom:12,fontSize:12,color:'#405147',lineHeight:1.6}}>{tc.data.q}</div>
            <button onClick={doPlay} disabled={playing} style={{width:'100%',padding:'9px',background:'#405147',color:'#F2EEE6',border:'none',borderRadius:10,fontFamily:"'Work Sans',sans-serif",fontSize:12,fontWeight:600,cursor:playing?'default':'pointer',opacity:playing?.7:1}}>{playing?'Playing…':'▶ Hear It'}</button></>)}
          {tc?.type==='sc'&&(<><div style={{fontFamily:"'Fraunces',serif",fontSize:22,fontWeight:700,color:'#405147',marginBottom:4}}>{tc.data.name}</div>
            <div style={{fontSize:11,color:'#9CB7B1',fontFamily:'monospace',marginBottom:8}}>{tc.data.steps}</div>
            <ScalePiano root={0} ivs={tc.data.ivs}/>
            <div style={{background:'white',borderRadius:10,padding:'10px 13px',marginBottom:6,fontSize:12,color:'#405147'}}>{tc.data.q}</div>
            <div style={{fontSize:11,color:'#9CB7B1',marginBottom:12}}>Characteristic: {tc.data.char}</div>
            <button onClick={doPlay} disabled={playing} style={{width:'100%',padding:'9px',background:'#405147',color:'#F2EEE6',border:'none',borderRadius:10,fontFamily:"'Work Sans',sans-serif",fontSize:12,fontWeight:600,cursor:playing?'default':'pointer',opacity:playing?.7:1}}>{playing?'Playing…':'▶ Hear It'}</button></>)}
          {tc?.type==='pg'&&(<><div style={{fontFamily:"'Fraunces',serif",fontSize:22,fontWeight:700,color:'#405147',marginBottom:6}}>{tc.data.name}</div>
            <div style={{background:'white',borderRadius:10,padding:'10px 13px',marginBottom:12,fontSize:12,color:'#405147',lineHeight:1.6}}>{tc.data.q}</div>
            <div style={{display:'flex',gap:6,flexWrap:'wrap',marginBottom:14}}>{tc.data.chs.map((c,i)=><span key={i} style={{background:'#D1E1DD',borderRadius:6,padding:'4px 8px',fontSize:11,fontWeight:600,color:'#405147'}}>{NOTES[c.o]}{CH[c.t].abbr}</span>)}</div></>)}
          {tc?.type==='mode'&&(<><div style={{fontFamily:"'Fraunces',serif",fontSize:22,fontWeight:700,color:'#405147',marginBottom:10}}>{tc.data.headline}</div>
            <div style={{fontSize:12,color:'#405147',lineHeight:1.7,marginBottom:14}}>{tc.data.body}</div>
            {tc.data.tips.map((t,i)=><div key={i} style={{display:'flex',gap:8,alignItems:'flex-start',marginBottom:6}}><div style={{width:5,height:5,borderRadius:'50%',background:'#C6A585',flexShrink:0,marginTop:5}}/><div style={{fontSize:12,color:'#405147'}}>{t}</div></div>)}</>)}
          {tc?.type==='key'&&(<><div style={{fontFamily:"'Fraunces',serif",fontSize:20,fontWeight:700,color:'#405147',marginBottom:8}}>Key Signatures</div>
            {KEY_STAGES[tc.stage].map(k=>{const ki=KEY_INFO[k];return ki?(<div key={k} style={{background:'white',borderRadius:10,padding:'9px 13px',marginBottom:6,display:'flex',justifyContent:'space-between'}}><div style={{fontWeight:600,fontSize:12,color:'#405147'}}>{ki.name}</div><div style={{fontSize:11,color:'#9CB7B1'}}>{ki.acc===0?'No sharps/flats':ki.acc>0?ki.acc+'♯':Math.abs(ki.acc)+'♭'}</div></div>):null;})}</>)}
          {!tc&&<div style={{color:'#9CB7B1',fontSize:13,textAlign:'center',padding:'20px 0'}}>Reference coming soon.</div>}
          <button onClick={onClose} style={{width:'100%',marginTop:16,padding:'9px',background:'transparent',border:'1.5px solid #BEC9A6',borderRadius:10,fontFamily:"'Work Sans',sans-serif",fontSize:12,fontWeight:600,color:'#405147',cursor:'pointer'}}>Close</button>
        </div>
      </div>
    </div>
  );
}

function LevelUp({data,onDone}){
  const[tutKey,setTutKey]=useState(null);
  if(!data)return null;
  const items=data.unlocks||[];
  const maxTier=Math.max(...items.map(u=>u.tier||1));
  const isFullScreen=maxTier>=4;
  const modeKey=items.find(u=>['chords','scales','progressions','tempo'].includes(u.type))?.type;
  const modeIntro=modeKey?MODE_INTRO[modeKey]:null;
  const modeName=data.modeName||'';
  if(isFullScreen)return(
    <div style={{position:'fixed',inset:0,background:'#405147',zIndex:60,display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',padding:'28px 24px',animation:'ri_fadeIn .3s'}}>
      <div style={{fontSize:52,marginBottom:16}}>🎉</div>
      {modeName&&<div style={{fontFamily:"'Work Sans',sans-serif",fontSize:10,fontWeight:700,letterSpacing:2,color:'#9CB7B1',textTransform:'uppercase',marginBottom:6}}>{modeName}</div>}
      <div style={{fontFamily:"'Fraunces',serif",fontSize:11,fontWeight:600,color:'#9CB7B1',letterSpacing:'0.15em',textTransform:'uppercase',marginBottom:8}}>Level {data.level}</div>
      <div style={{fontFamily:"'Fraunces',serif",fontSize:28,fontWeight:700,color:'#F2EEE6',textAlign:'center',marginBottom:8,lineHeight:1.2}}>{items[0]?.name}</div>
      <div style={{fontSize:13,color:'#BEC9A6',textAlign:'center',marginBottom:24,maxWidth:320,lineHeight:1.6}}>{items[0]?.desc}</div>
      {modeIntro&&<div style={{background:'rgba(255,255,255,.08)',borderRadius:14,padding:'14px 16px',marginBottom:20,maxWidth:340,width:'100%'}}><div style={{fontFamily:"'Fraunces',serif",fontSize:14,fontWeight:700,color:'#C6A585',marginBottom:6}}>{modeIntro.headline}</div><div style={{fontSize:12,color:'#BEC9A6',lineHeight:1.6,marginBottom:8}}>{modeIntro.body}</div>{modeIntro.tips.map((t,i)=><div key={i} style={{display:'flex',gap:8,marginBottom:4}}><div style={{color:'#C6A585',fontSize:10,marginTop:2}}>▸</div><div style={{fontSize:11,color:'#BEC9A6'}}>{t}</div></div>)}</div>}
      <button onClick={onDone} style={{background:'#C6A585',color:'white',border:'none',borderRadius:12,padding:'13px 32px',fontFamily:"'Work Sans',sans-serif",fontSize:14,fontWeight:700,cursor:'pointer'}}>Got it →</button>
      {tutKey&&<TutorialSheet tutKey={tutKey} onClose={()=>setTutKey(null)}/>}
    </div>
  );
  return(
    <div style={{position:'fixed',inset:0,background:'rgba(64,81,71,.55)',zIndex:60,display:'flex',alignItems:'center',justifyContent:'center',padding:'20px',animation:'ri_fadeIn .2s'}}>
      <div style={{background:'#F2EEE6',borderRadius:20,padding:'22px 20px',maxWidth:360,width:'100%',boxShadow:'0 8px 40px rgba(64,81,71,.35)',animation:'ri_scaleIn .25s'}}>
        <div style={{display:'flex',alignItems:'center',gap:10,marginBottom:12}}>
          <div style={{background:'#405147',borderRadius:'50%',width:36,height:36,display:'flex',alignItems:'center',justifyContent:'center',flexShrink:0}}><span style={{color:'#F2EEE6',fontSize:14,fontWeight:700}}>{data.level}</span></div>
          <div><div style={{fontFamily:"'Fraunces',serif",fontSize:11,fontWeight:600,color:'#9CB7B1',letterSpacing:'0.12em',textTransform:'uppercase'}}>Level Up</div>{modeName&&<div style={{fontSize:10,color:'#C6A585',fontWeight:600}}>{modeName}</div>}</div>
        </div>
        {items.map((u,i)=>(<div key={i} style={{marginBottom:10}}><div style={{fontFamily:"'Fraunces',serif",fontSize:17,fontWeight:700,color:'#405147',marginBottom:2}}>{u.name}</div><div style={{fontSize:12,color:'#9CB7B1',lineHeight:1.5}}>{u.desc}</div>{u.tutKey&&<button onClick={()=>setTutKey(u.tutKey)} style={{marginTop:6,background:'transparent',border:'none',color:'#C6A585',fontFamily:"'Work Sans',sans-serif",fontSize:11,fontWeight:600,cursor:'pointer',padding:0}}>Learn More →</button>}</div>))}
        <button onClick={onDone} style={{width:'100%',marginTop:10,padding:'10px',background:'#405147',color:'#F2EEE6',border:'none',borderRadius:10,fontFamily:"'Work Sans',sans-serif",fontSize:12,fontWeight:700,cursor:'pointer'}}>Got it</button>
      </div>
      {tutKey&&<TutorialSheet tutKey={tutKey} onClose={()=>setTutKey(null)}/>}
    </div>
  );
}

function WelcomeScreen({onDone}){
  const[name,setName]=useState('');const[step,setStep]=useState(0);
  return(
    <div style={{position:'fixed',inset:0,background:'#405147',display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',padding:'32px 24px',zIndex:100}}>
      {step===0&&(<>
        <div style={{fontSize:48,marginBottom:20}}>🎵</div>
        <div style={{fontFamily:"'Fraunces',serif",fontSize:36,fontWeight:700,color:'#F2EEE6',textAlign:'center',lineHeight:1.1,marginBottom:10}}>Welcome to<br/><em style={{fontStyle:'italic',color:'#C6A585'}}>Rhythmic.</em></div>
        <div style={{fontSize:13,color:'#9CB7B1',textAlign:'center',maxWidth:320,lineHeight:1.8,marginBottom:10}}>A mindful ear training space for music students. Train your ear across intervals, chords, scales, progressions, and tempo.</div>
        <div style={{background:'rgba(255,255,255,.07)',borderRadius:14,padding:'16px 18px',maxWidth:320,width:'100%',marginBottom:28}}>
          {['Each exercise mode has its own level — progress at your own pace per subject.','Sessions are intentionally limited — quality over quantity.','Your daily score and streak reset each day to keep things fresh.'].map((t,i)=>(
            <div key={i} style={{display:'flex',gap:10,marginBottom:i<2?10:0}}><div style={{width:5,height:5,borderRadius:'50%',background:'#C6A585',flexShrink:0,marginTop:6}}/><div style={{fontSize:12,color:'#BEC9A6',lineHeight:1.6}}>{t}</div></div>
          ))}
        </div>
        <button onClick={()=>setStep(1)} style={{background:'#C6A585',color:'white',border:'none',borderRadius:12,padding:'14px 40px',fontFamily:"'Work Sans',sans-serif",fontSize:15,fontWeight:700,cursor:'pointer'}}>Get Started →</button>
      </>)}
      {step===1&&(<>
        <div style={{fontFamily:"'Fraunces',serif",fontSize:26,fontWeight:700,color:'#F2EEE6',textAlign:'center',marginBottom:8}}>What should we call you?</div>
        <div style={{fontSize:12,color:'#9CB7B1',marginBottom:24,textAlign:'center'}}>Your name appears on the daily leaderboard.</div>
        <input value={name} onChange={e=>setName(e.target.value)} placeholder='Your name…' style={{width:'100%',maxWidth:300,padding:'13px 16px',borderRadius:12,border:'2px solid #9CB7B1',background:'rgba(255,255,255,.1)',color:'#F2EEE6',fontFamily:"'Work Sans',sans-serif",fontSize:15,outline:'none',boxSizing:'border-box',textAlign:'center'}} onKeyDown={e=>e.key==='Enter'&&name.trim()&&onDone(name.trim())}/>
        <button onClick={()=>name.trim()&&onDone(name.trim())} disabled={!name.trim()} style={{marginTop:16,background:name.trim()?'#C6A585':'rgba(255,255,255,.15)',color:'white',border:'none',borderRadius:12,padding:'13px 36px',fontFamily:"'Work Sans',sans-serif",fontSize:14,fontWeight:700,cursor:name.trim()?'pointer':'default'}}>Begin Training →</button>
        <button onClick={()=>onDone('')} style={{marginTop:10,background:'transparent',border:'none',color:'#9CB7B1',fontSize:11,cursor:'pointer',fontFamily:"'Work Sans',sans-serif"}}>Skip for now</button>
      </>)}
    </div>
  );
}

function ExerciseModeIntro({mode,onBegin}){
  const d=EXERCISE_INTROS[mode];if(!d)return null;
  return(
    <div style={{position:'absolute',inset:0,background:'#F2EEE6',zIndex:30,overflowY:'auto',display:'flex',flexDirection:'column'}}>
      <div style={{background:'#405147',padding:'22px 20px 18px',boxShadow:'0 2px 8px rgba(64,81,71,.2)'}}>
        <div style={{fontFamily:"'Fraunces',serif",fontSize:26,fontWeight:700,color:'#F2EEE6',lineHeight:1}}>{d.icon} {d.headline}</div>
        <div style={{fontSize:11,color:'#9CB7B1',marginTop:4}}>Understanding the exercise</div>
      </div>
      <div style={{padding:'20px 20px 32px',flex:1}}>
        {[{label:'What it is',text:d.what,color:'#D1E1DD'},{label:'How it works',text:d.how,color:'#BEC9A6'},{label:'Why it matters',text:d.why,color:'#C6A585'},{label:'An example',text:d.example,color:'#9CB7B1'}].map(({label,text,color})=>(<div key={label} style={{marginBottom:14}}><div style={{display:'flex',alignItems:'center',gap:6,marginBottom:6}}><div style={{width:10,height:10,borderRadius:3,background:color,flexShrink:0}}/><div style={{fontFamily:"'Fraunces',serif",fontSize:13,fontWeight:700,color:'#405147'}}>{label}</div></div><div style={{background:'white',borderRadius:10,padding:'11px 14px',fontSize:12,color:'#405147',lineHeight:1.7}}>{text}</div></div>))}
        <button onClick={onBegin} style={{width:'100%',marginTop:8,padding:'14px',background:'#405147',color:'#F2EEE6',border:'none',borderRadius:12,fontFamily:"'Work Sans',sans-serif",fontSize:14,fontWeight:700,cursor:'pointer'}}>Begin Practice →</button>
      </div>
    </div>
  );
}

const LIB_TABS=[{id:'intervals',label:'Intervals',icon:'↔'},{id:'chords',label:'Chords',icon:'♪'},{id:'scales',label:'Scales',icon:'〜'},{id:'keys',label:'Keys',icon:'🗝'},{id:'progressions',label:'Progs',icon:'♫'}];
function LibraryScreen({xpByMode,onBack}){
  const[tab,setTab]=useState('intervals');
  const[openTut,setOpenTut]=useState(null);
  const uc=getContent(xpByMode);
  const ivSet=new Set(uc.intervals.pool);const chSet=new Set(uc.chords.pool);const scSet=new Set(uc.scales.pool);const pgSet=new Set(uc.progressions.pool);
  const maxKS=Math.max(uc.intervals.keyStage,uc.chords.keyStage,uc.scales.keyStage,uc.progressions.keyStage);
  const Row=({children,onClick})=>(<div onClick={onClick} style={{display:'flex',alignItems:'center',background:'white',borderRadius:12,padding:'11px 14px',marginBottom:8,border:'1.5px solid #BEC9A6',cursor:'pointer'}}>{children}</div>);
  const Locked=({msg})=>(<div style={{textAlign:'center',padding:'44px 20px',color:'#9CB7B1'}}><div style={{fontSize:38,marginBottom:10}}>🔒</div><div style={{fontFamily:"'Fraunces',serif",fontSize:14,fontWeight:600,color:'#405147',marginBottom:5}}>{msg}</div><div style={{fontSize:11}}>Keep practising to unlock this section.</div></div>);
  return(
    <div style={{background:'#F2EEE6',minHeight:'100vh',maxWidth:430,margin:'0 auto',display:'flex',flexDirection:'column'}}>
      <div style={{background:'#405147',padding:'22px 20px 16px',boxShadow:'0 2px 8px rgba(64,81,71,.2)'}}>
        <button onClick={onBack} style={{background:'transparent',border:'none',color:'#9CB7B1',fontFamily:"'Work Sans',sans-serif",fontSize:12,fontWeight:600,cursor:'pointer',padding:0,marginBottom:6}}>← Back</button>
        <div style={{fontFamily:"'Fraunces',serif",fontSize:22,fontWeight:700,color:'#F2EEE6',lineHeight:1}}>Music <em style={{fontStyle:'italic',color:'#C6A585'}}>Library</em></div>
        <div style={{fontSize:11,color:'#9CB7B1',marginTop:3}}>Reference for everything you have unlocked</div>
      </div>
      <div style={{display:'flex',background:'white',borderBottom:'1.5px solid #BEC9A6',overflowX:'auto'}}>
        {LIB_TABS.map(t=>(<button key={t.id} onClick={()=>setTab(t.id)} style={{flex:'0 0 auto',padding:'9px 12px',border:'none',background:'transparent',fontFamily:"'Work Sans',sans-serif",fontSize:10,fontWeight:600,color:tab===t.id?'#405147':'#9CB7B1',cursor:'pointer',borderBottom:'2.5px solid '+(tab===t.id?'#405147':'transparent'),whiteSpace:'nowrap'}}>{t.icon} {t.label}</button>))}
      </div>
      <div style={{overflowY:'auto',padding:'14px 16px 28px',flex:1}}>
        {tab==='intervals'&&(<>{ivSet.size===0?<Locked msg='No intervals unlocked yet'/>:IV.filter(iv=>ivSet.has(iv.id)).map(iv=>(<Row key={iv.id} onClick={()=>setOpenTut('iv-'+iv.id)}><div style={{flex:1}}><div style={{fontFamily:"'Fraunces',serif",fontSize:14,fontWeight:700,color:'#405147'}}>{iv.name}</div><div style={{fontSize:11,color:'#9CB7B1',marginTop:2}}>{iv.id} semitone{iv.id!==1?'s':''}</div></div><div style={{display:'flex',gap:6,alignItems:'center'}}><span style={{background:'#D1E1DD',borderRadius:5,padding:'2px 7px',fontSize:10,fontWeight:700,color:'#405147'}}>{iv.abbr}</span><span style={{color:'#9CB7B1',fontSize:12}}>›</span></div></Row>))}</>)}
        {tab==='chords'&&(<>{!uc.chords.on?<Locked msg='Chords unlock at Intervals Level 20'/>:Object.values(CH).filter(ch=>chSet.has(ch.id)).map(ch=>(<Row key={ch.id} onClick={()=>setOpenTut('ch-'+ch.id)}><div style={{flex:1}}><div style={{fontFamily:"'Fraunces',serif",fontSize:14,fontWeight:700,color:'#405147'}}>{ch.name}</div><div style={{fontSize:11,color:'#9CB7B1',marginTop:2}}>{ch.formula}</div></div><div style={{display:'flex',gap:6,alignItems:'center'}}><span style={{background:'#D1E1DD',borderRadius:5,padding:'2px 7px',fontSize:10,fontWeight:700,color:'#405147'}}>{ch.abbr}</span><span style={{color:'#9CB7B1',fontSize:12}}>›</span></div></Row>))}</>)}
        {tab==='scales'&&(<>{!uc.scales.on?<Locked msg='Scales unlock at Intervals Level 10'/>:SC.filter(sc=>scSet.has(sc.id)).map(sc=>(<Row key={sc.id} onClick={()=>setOpenTut('sc-'+sc.id)}><div style={{flex:1}}><div style={{fontFamily:"'Fraunces',serif",fontSize:14,fontWeight:700,color:'#405147'}}>{sc.name}</div><div style={{fontSize:11,color:'#9CB7B1',marginTop:2,fontFamily:'monospace'}}>{sc.steps}</div></div><span style={{color:'#9CB7B1',fontSize:12}}>›</span></Row>))}</>)}
        {tab==='keys'&&(<>{maxKS===0?<Locked msg='Key signatures unlock through practice'/>:KEY_STAGES[maxKS].map(k=>{const ki=KEY_INFO[k];if(!ki)return null;return(<Row key={k} onClick={()=>setOpenTut('key-stage-1')}><div style={{flex:1}}><div style={{fontFamily:"'Fraunces',serif",fontSize:14,fontWeight:700,color:'#405147'}}>{ki.name}</div><div style={{fontSize:11,color:'#9CB7B1',marginTop:2}}>{ki.acc===0?'No sharps or flats':ki.acc>0?`${ki.acc} sharp${ki.acc>1?'s':''}: ${ki.notes.join(', ')}`:`${Math.abs(ki.acc)} flat${Math.abs(ki.acc)>1?'s':''}: ${ki.notes.join(', ')}`}</div></div><span style={{color:'#9CB7B1',fontSize:12}}>›</span></Row>);})}</>)}
        {tab==='progressions'&&(<>{!uc.progressions.on?<Locked msg='Progressions unlock at Chords Level 10'/>:PG.filter(pg=>pgSet.has(pg.id)).map(pg=>(<Row key={pg.id} onClick={()=>setOpenTut('pg-'+pg.id)}><div style={{flex:1}}><div style={{fontFamily:"'Fraunces',serif",fontSize:14,fontWeight:700,color:'#405147'}}>{pg.name}</div><div style={{fontSize:11,color:'#9CB7B1',marginTop:2}}>{pg.q}</div></div><span style={{color:'#9CB7B1',fontSize:12}}>›</span></Row>))}</>)}
      </div>
      {openTut&&<TutorialSheet tutKey={openTut} onClose={()=>setOpenTut(null)}/>}
    </div>
  );
}

const MODE_LABELS={intervals:{icon:'↔',label:'Intervals'},chords:{icon:'♪',label:'Chords'},scales:{icon:'〜',label:'Scales'},progressions:{icon:'♫',label:'Progressions'},tempo:{icon:'♩',label:'Tempo'}};
function RoadmapSheet({mode,currentLevel,onClose}){
  const unlocks=UNLOCKS_BY_MODE[mode]||[];
  const ml=MODE_LABELS[mode]||{icon:'',label:mode};
  return(<div style={{position:'fixed',inset:0,background:'rgba(64,81,71,.5)',zIndex:40,display:'flex',alignItems:'flex-end',animation:'ri_fadeIn .2s'}} onClick={e=>e.target===e.currentTarget&&onClose()}>
    <div style={{background:'#F2EEE6',width:'100%',maxWidth:430,margin:'0 auto',borderRadius:'22px 22px 0 0',maxHeight:'88vh',display:'flex',flexDirection:'column',animation:'ri_slideSheet .3s'}}>
      <div style={{width:34,height:4,background:'#BEC9A6',borderRadius:2,margin:'10px auto 0'}}/>
      <div style={{padding:'14px 20px 10px',borderBottom:'1px solid #BEC9A6',display:'flex',justifyContent:'space-between',alignItems:'center'}}>
        <div><div style={{fontFamily:"'Fraunces',serif",fontSize:18,fontWeight:700,color:'#405147'}}>{ml.icon} {ml.label} Roadmap</div><div style={{fontSize:10,color:'#9CB7B1',marginTop:2}}>Level {currentLevel} of {MAX_LV}</div></div>
        <button onClick={onClose} style={{background:'transparent',border:'none',color:'#9CB7B1',fontSize:18,cursor:'pointer'}}>✕</button>
      </div>
      <div style={{overflowY:'auto',padding:'12px 18px 28px'}}>
        {unlocks.map((u,i)=>(<div key={i} style={{display:'flex',gap:10,marginBottom:8,opacity:u.lv>currentLevel?.45:1}}>
          <div style={{width:28,height:28,borderRadius:'50%',background:u.lv<=currentLevel?'#405147':'#BEC9A6',display:'flex',alignItems:'center',justifyContent:'center',flexShrink:0,marginTop:2}}>
            <span style={{fontSize:8,fontWeight:700,color:'white'}}>{u.lv}</span>
          </div>
          <div style={{flex:1,paddingTop:3}}>
            <div style={{fontSize:12,fontWeight:700,color:u.lv<=currentLevel?'#405147':'#9CB7B1',fontFamily:"'Fraunces',serif"}}>{u.lv<=currentLevel?'✓ ':''}{u.name||'Practice'}</div>
            {u.desc&&<div style={{fontSize:10,color:'#9CB7B1',marginTop:1,lineHeight:1.4}}>{u.desc}</div>}
          </div>
        </div>))}
      </div>
    </div>
  </div>);
}

// Global stats — shown from Hub: daily score, score history, leaderboard
function GlobalStatsSheet({history,lb,profile,dailyScore,onClose}){
  const[tab,setTab]=useState('history');
  return(<div style={{position:'fixed',inset:0,background:'rgba(64,81,71,.5)',zIndex:40,display:'flex',alignItems:'flex-end',animation:'ri_fadeIn .2s'}} onClick={e=>e.target===e.currentTarget&&onClose()}>
    <div style={{background:'#F2EEE6',width:'100%',maxWidth:430,margin:'0 auto',borderRadius:'22px 22px 0 0',maxHeight:'88vh',display:'flex',flexDirection:'column',animation:'ri_slideSheet .3s'}}>
      <div style={{width:34,height:4,background:'#BEC9A6',borderRadius:2,margin:'10px auto 0'}}/>
      <div style={{padding:'14px 20px 10px',borderBottom:'1px solid #BEC9A6',display:'flex',justifyContent:'space-between',alignItems:'center'}}>
        <div style={{fontFamily:"'Fraunces',serif",fontSize:18,fontWeight:700,color:'#405147'}}>Statistics</div>
        <button onClick={onClose} style={{background:'transparent',border:'none',color:'#9CB7B1',fontSize:18,cursor:'pointer'}}>✕</button>
      </div>
      <div style={{display:'flex',borderBottom:'1px solid #BEC9A6'}}>
        {['history','board'].map(t=>(<button key={t} onClick={()=>setTab(t)} style={{flex:1,padding:'9px',border:'none',background:'transparent',fontFamily:"'Work Sans',sans-serif",fontSize:11,fontWeight:600,color:tab===t?'#405147':'#9CB7B1',borderBottom:'2px solid '+(tab===t?'#405147':'transparent'),cursor:'pointer'}}>{t==='board'?'Leaderboard':'Score History'}</button>))}
      </div>
      <div style={{overflowY:'auto',padding:'14px 18px 28px'}}>
        <div style={{background:'white',borderRadius:12,padding:'14px 16px',marginBottom:12,display:'flex',justifyContent:'space-between',alignItems:'center'}}>
          <div style={{fontSize:11,color:'#9CB7B1'}}>Today</div>
          <div style={{fontFamily:"'Fraunces',serif",fontSize:28,fontWeight:700,color:'#405147'}}>{(dailyScore||0).toLocaleString()}</div>
        </div>
        {tab==='history'&&(history.length===0
          ?<div style={{textAlign:'center',padding:'32px 0',color:'#9CB7B1',fontSize:12}}>No history yet. Keep practising.</div>
          :history.slice().reverse().map((e,i)=>(<div key={i} style={{display:'flex',justifyContent:'space-between',padding:'8px 0',borderBottom:'1px solid #BEC9A6'}}>
            <div style={{fontSize:12,color:'#9CB7B1'}}>{e.date}</div>
            <div style={{fontFamily:"'Fraunces',serif",fontSize:13,fontWeight:700,color:'#405147'}}>{e.total.toLocaleString()}</div>
          </div>))
        )}
        {tab==='board'&&(lb.length===0
          ?<div style={{textAlign:'center',padding:'32px 0',color:'#9CB7B1',fontSize:12}}>No scores yet today.</div>
          :lb.map((e,i)=>(<div key={i} style={{display:'flex',alignItems:'center',gap:8,padding:'8px 0',borderBottom:'1px solid #BEC9A6'}}>
            <span style={{fontSize:12,fontWeight:700,color:i===0?'#c9a227':i===1?'#9CB7B1':i===2?'#C6A585':'#bbb',minWidth:20}}>{i===0?'🥇':i===1?'🥈':i===2?'🥉':'#'+(i+1)}</span>
            <span style={{flex:1,fontSize:12,fontWeight:600,color:'#405147'}}>{e.name}</span>
            <span style={{fontFamily:"'Fraunces',serif",fontSize:13,fontWeight:700,color:'#405147'}}>{(e.total||0).toLocaleString()}</span>
          </div>))
        )}
      </div>
    </div>
  </div>);
}

// Per-mode stats — shown from EarTraining header: accuracy + answer breakdown for this subject
function ModeStatsSheet({mode,stats,onClose}){
  const s=stats[mode]||{s:0,f:0};
  const total=s.s+s.f;
  const acc=total>0?Math.round(s.s/total*100):null;
  const ml=MODE_LABELS[mode]||{icon:'',label:mode};
  return(<div style={{position:'fixed',inset:0,background:'rgba(64,81,71,.5)',zIndex:40,display:'flex',alignItems:'flex-end',animation:'ri_fadeIn .2s'}} onClick={e=>e.target===e.currentTarget&&onClose()}>
    <div style={{background:'#F2EEE6',width:'100%',maxWidth:430,margin:'0 auto',borderRadius:'22px 22px 0 0',maxHeight:'60vh',display:'flex',flexDirection:'column',animation:'ri_slideSheet .3s'}}>
      <div style={{width:34,height:4,background:'#BEC9A6',borderRadius:2,margin:'10px auto 0'}}/>
      <div style={{padding:'14px 20px 10px',borderBottom:'1px solid #BEC9A6',display:'flex',justifyContent:'space-between',alignItems:'center'}}>
        <div>
          <div style={{fontFamily:"'Fraunces',serif",fontSize:18,fontWeight:700,color:'#405147'}}>{ml.icon} {ml.label}</div>
          <div style={{fontSize:10,color:'#9CB7B1',marginTop:2}}>Today's session accuracy</div>
        </div>
        <button onClick={onClose} style={{background:'transparent',border:'none',color:'#9CB7B1',fontSize:18,cursor:'pointer'}}>✕</button>
      </div>
      <div style={{padding:'20px 20px 32px'}}>
        {total===0
          ?<div style={{textAlign:'center',padding:'24px 0',color:'#9CB7B1',fontSize:12}}>No answers yet this session.</div>
          :(<>
            {/* Accuracy ring display */}
            <div style={{display:'flex',alignItems:'center',gap:20,marginBottom:20}}>
              <div style={{position:'relative',width:72,height:72,flexShrink:0}}>
                <svg width={72} height={72} viewBox='0 0 72 72'>
                  <circle cx={36} cy={36} r={28} fill='none' stroke='#BEC9A6' strokeWidth={6}/>
                  <circle cx={36} cy={36} r={28} fill='none' stroke='#405147' strokeWidth={6}
                    strokeDasharray={`${2*Math.PI*28}`}
                    strokeDashoffset={`${2*Math.PI*28*(1-(acc||0)/100)}`}
                    strokeLinecap='round'
                    transform='rotate(-90 36 36)'/>
                </svg>
                <div style={{position:'absolute',inset:0,display:'flex',alignItems:'center',justifyContent:'center',fontFamily:"'Fraunces',serif",fontSize:16,fontWeight:700,color:'#405147'}}>{acc}%</div>
              </div>
              <div>
                <div style={{fontFamily:"'Fraunces',serif",fontSize:13,fontWeight:700,color:'#405147',marginBottom:6}}>Accuracy</div>
                <div style={{fontSize:11,color:'#9CB7B1',marginBottom:3}}>✓ {s.s} correct</div>
                <div style={{fontSize:11,color:'#9CB7B1',marginBottom:3}}>✗ {s.f} wrong</div>
                <div style={{fontSize:11,color:'#9CB7B1'}}>{total} attempts total</div>
              </div>
            </div>
            {/* Precision bar */}
            <div style={{background:'white',borderRadius:12,padding:'12px 14px'}}>
              <div style={{fontSize:10,color:'#9CB7B1',fontWeight:600,marginBottom:8,textTransform:'uppercase',letterSpacing:.5}}>Precision</div>
              <div style={{height:8,background:'#BEC9A6',borderRadius:4,overflow:'hidden'}}>
                <div style={{height:'100%',width:acc+'%',background:acc>=80?'#405147':acc>=60?'#C6A585':'#9CB7B1',borderRadius:4,transition:'width .6s ease'}}/>
              </div>
              <div style={{fontSize:10,color:'#9CB7B1',marginTop:6}}>{acc>=80?'Strong — keep building.':acc>=60?'Developing — stay focused.':'Early stages — trust the process.'}</div>
            </div>
          </>)
        }
      </div>
    </div>
  </div>);
}

const Styles=()=>(<style>{`
  @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,700;1,400;1,700&family=Work+Sans:wght@400;600;700&display=swap');
  *{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent;}
  body,#root{background:#F2EEE6;font-family:'Work Sans',sans-serif;}
  @keyframes ri_fadeIn{from{opacity:0}to{opacity:1}}
  @keyframes ri_slideSheet{from{transform:translateY(60px);opacity:0}to{transform:translateY(0);opacity:1}}
  @keyframes ri_scaleIn{from{transform:scale(.92);opacity:0}to{transform:scale(1);opacity:1}}
  @keyframes ri_bounce{0%,100%{transform:scale(1)}50%{transform:scale(1.18)}}
  @keyframes ri_playFill{from{width:0%}to{width:100%}}
  @keyframes ri_waveA{0%,100%{height:4px}50%{height:14px}}
  @keyframes ri_waveB{0%,100%{height:8px}50%{height:20px}}
  @keyframes ri_waveC{0%,100%{height:6px}50%{height:16px}}
  /* ── root layout ── */
  .r-root{background:#F2EEE6;min-height:100dvh;max-width:430px;margin:0 auto;display:flex;flex-direction:column;position:relative;}
  .r-scroll{flex:1;overflow-y:auto;padding-bottom:24px;}
  /* ── header ── */
  .r-hdr{background:#405147;padding:14px 16px 12px;box-shadow:0 2px 12px rgba(64,81,71,.25);flex-shrink:0;}
  .hdr-row1{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;}
  .hdr-back{background:transparent;border:none;color:#9CB7B1;font-family:'Work Sans',sans-serif;font-size:12px;font-weight:600;cursor:pointer;padding:0;display:flex;align-items:center;gap:4px;min-width:40px;}
  .hdr-title{font-family:'Fraunces',serif;font-size:15px;font-weight:700;color:#F2EEE6;text-align:center;flex:1;}
  .hdr-actions{display:flex;gap:8px;min-width:40px;justify-content:flex-end;}
  .hdr-icon-btn{background:transparent;border:none;color:#9CB7B1;font-size:15px;cursor:pointer;padding:2px;}
  .hdr-xp-row{display:flex;align-items:center;gap:8px;margin-bottom:7px;}
  .hdr-lv{font-family:'Fraunces',serif;font-size:12px;font-weight:700;color:'#C6A585';white-space:nowrap;min-width:36px;}
  .hdr-bar-wrap{flex:1;height:5px;background:rgba(255,255,255,.15);border-radius:3px;overflow:hidden;}
  .hdr-bar-fill{height:100%;background:#C6A585;border-radius:3px;transition:width .5s ease;}
  .hdr-xp-frac{font-size:9px;color:rgba(156,183,177,.8);white-space:nowrap;}
  .hdr-meta-row{display:flex;align-items:center;justify-content:space-between;}
  .hdr-streak{font-size:10px;color:#C6A585;font-weight:600;}
  .hdr-score{font-size:10px;color:rgba(156,183,177,.8);font-weight:600;}
  /* ── mode nav ── */
  .r-nav{display:flex;background:white;border-bottom:1.5px solid #BEC9A6;overflow-x:auto;flex-shrink:0;}
  .r-nav-btn{flex:0 0 auto;padding:9px 10px;border:none;background:transparent;font-family:'Work Sans',sans-serif;font-size:10px;font-weight:600;color:#9CB7B1;cursor:pointer;border-bottom:2.5px solid transparent;white-space:nowrap;transition:color .15s,border-color .15s;}
  .r-nav-btn.active{color:#405147;border-bottom-color:#405147;}
  .r-nav-btn.done{color:#BEC9A6;}
  .r-nav-btn.locked{opacity:.35;cursor:default;}
  /* ── attempt bar ── */
  .att-bar-wrap{padding:5px 16px 0;flex-shrink:0;}
  .att-bar-track{height:3px;background:#BEC9A6;border-radius:2px;overflow:hidden;}
  .att-bar-fill{height:100%;background:#405147;border-radius:2px;transition:width .4s ease;}
  /* ── question card ── */
  .r-qcard{background:white;border-radius:16px;padding:18px 16px;margin:14px 16px 0;box-shadow:0 2px 12px rgba(64,81,71,.07);}
  /* ── play button ── */
  .play-btn{display:flex;align-items:center;justify-content:center;gap:6px;width:100%;padding:11px;background:#405147;color:#F2EEE6;border:none;border-radius:10px;font-family:'Work Sans',sans-serif;font-size:12px;font-weight:600;cursor:pointer;position:relative;overflow:hidden;margin-top:10px;}
  .play-btn:disabled{opacity:.85;cursor:default;}
  .play-fill{position:absolute;left:0;top:0;height:100%;background:rgba(255,255,255,.2);pointer-events:none;}
  .play-btn-inner{position:relative;z-index:1;display:flex;align-items:center;gap:6px;}
  .wave-bars{display:flex;gap:2px;align-items:center;height:20px;}
  .wave-bar{width:3px;border-radius:2px;background:#9CB7B1;}
  .wb1{animation:ri_waveA .7s ease-in-out infinite;}
  .wb2{animation:ri_waveB .7s ease-in-out infinite .1s;}
  .wb3{animation:ri_waveC .7s ease-in-out infinite .2s;}
  .wb4{animation:ri_waveB .7s ease-in-out infinite .3s;}
  .wb5{animation:ri_waveA .7s ease-in-out infinite .15s;}
  /* ── choices ── */
  .r-choices{padding:10px 16px 0;}
  .choices-lbl{font-size:10px;font-weight:600;color:#9CB7B1;text-transform:uppercase;letter-spacing:.1em;margin-bottom:8px;}
  .choices-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:8px;}
  .cbtn{background:white;border:2px solid #BEC9A6;border-radius:12px;padding:11px 8px;font-family:'Work Sans',sans-serif;font-size:11px;font-weight:600;color:#405147;cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:3px;transition:border-color .12s,background .12s;}
  .cbtn:disabled{cursor:default;}
  .cbtn.correct{border-color:#405147;background:#405147;color:#F2EEE6;}
  .cbtn.wrong{border-color:#C6A585;background:rgba(198,165,133,.12);}
  .cabbr{font-size:9px;font-weight:700;opacity:.7;}
  /* ── done banner ── */
  .done-banner{background:white;border-radius:14px;padding:22px;margin:16px;text-align:center;border:1.5px dashed #BEC9A6;}
  /* ── bounce msg ── */
  .bounce-msg{text-align:center;font-family:'Fraunces',serif;font-size:15px;font-weight:700;padding:4px 0 6px;animation:ri_bounce .35s ease;}
  /* ── notes row ── */
  .notes-row{display:flex;align-items:center;justify-content:center;gap:10px;margin-bottom:8px;}
  .npill{background:#F2EEE6;border:1.5px solid #BEC9A6;border-radius:8px;padding:5px 10px;text-align:center;}
  .npa{border-color:#9CB7B1;background:#D1E1DD;}
  .npb{border-color:#C6A585;background:rgba(198,165,133,.15);}
  .nnm{font-family:'Fraunces',serif;font-size:16px;font-weight:700;color:#405147;}
  .nsub{font-size:9px;color:#9CB7B1;}
  .m-icon{font-size:36px;display:block;margin:8px auto 6px;text-align:center;}
  .info-chip{background:#D1E1DD;border-radius:20px;padding:4px 12px;font-size:11px;color:#405147;font-weight:600;display:block;width:fit-content;margin:0 auto 8px;}
  /* ── tempo ── */
  .tempo-wrap{display:flex;gap:8px;margin-top:10px;}
  .tempo-in{flex:1;padding:9px 12px;border:2px solid #BEC9A6;border-radius:10px;font-family:'Work Sans',sans-serif;font-size:14px;font-weight:600;color:#405147;background:white;outline:none;}
  .tempo-in:focus{border-color:#405147;}
  .tempo-sub{padding:9px 16px;background:#405147;color:#F2EEE6;border:none;border-radius:10px;font-family:'Work Sans',sans-serif;font-size:12px;font-weight:600;cursor:pointer;}
  .tempo-sub:disabled{opacity:.5;cursor:default;}
`}</style>);

const MODE_DEFS=[
  {id:'intervals',   icon:'↔', label:'Intervals',    desc:'The building blocks — distance between two notes.'},
  {id:'chords',      icon:'♪', label:'Chords',       desc:'Three or more notes combined — harmony in a moment.',  req:'Intervals Lv 20'},
  {id:'scales',      icon:'〜',label:'Scales',        desc:'Seven notes that feel like home — melody lives here.',  req:'Intervals Lv 10'},
  {id:'progressions',icon:'♫', label:'Progressions', desc:'Chords in motion — the harmonic sentence.',             req:'Chords Lv 10'},
  {id:'tempo',       icon:'♩', label:'Tempo',        desc:'The pulse — BPM recognition and inner metronome.',      req:'Intervals Lv 8'},
];
function SubjectHub({xpByMode,profile,lb,history,dailyScore,dailyAttempts,onSelect}){
  const[showGlobalStats,setShowGlobalStats]=useState(false);
  const content=getContent(xpByMode);
  const ml=content.modeLevels;
  const myRank=Array.isArray(lb)?lb.findIndex(e=>e.id===profile?.id)+1:0;
  return(
    <div style={{background:'#F2EEE6',minHeight:'100dvh',maxWidth:430,margin:'0 auto',display:'flex',flexDirection:'column',overflowY:'auto'}}>
      {/* Hub header */}
      <div style={{background:'#405147',padding:'22px 20px 18px',boxShadow:'0 2px 12px rgba(64,81,71,.2)'}}>
        <div style={{display:'flex',alignItems:'flex-start',justifyContent:'space-between',marginBottom:16}}>
          <div>
            <div style={{fontFamily:"'Fraunces',serif",fontSize:28,fontWeight:700,color:'#F2EEE6',lineHeight:1}}>Rhythmic<em style={{fontStyle:'italic',color:'#C6A585'}}>.</em></div>
            {profile?.name&&<div style={{fontSize:10,color:'#9CB7B1',marginTop:3}}>Welcome back, {profile.name}</div>}
          </div>
          <div style={{display:'flex',flexDirection:'column',alignItems:'flex-end',gap:4}}>
            <button onClick={()=>setShowGlobalStats(true)} style={{background:'rgba(255,255,255,.08)',border:'none',borderRadius:8,padding:'5px 10px',cursor:'pointer',display:'flex',alignItems:'center',gap:5}}>
              <span style={{fontSize:12}}>📊</span>
              <span style={{fontFamily:"'Work Sans',sans-serif",fontSize:9,fontWeight:600,color:'#9CB7B1',letterSpacing:.5}}>Stats</span>
            </button>
            <div style={{textAlign:'right'}}>
              <div style={{fontFamily:"'Fraunces',serif",fontSize:22,fontWeight:700,color:'#C6A585',lineHeight:1}}>{(dailyScore||0).toLocaleString()}</div>
              <div style={{fontSize:9,color:'#9CB7B1',marginTop:2,letterSpacing:.5,textTransform:'uppercase'}}>Today{myRank>0?` · #${myRank}`:''}</div>
              {profile?.streak>0&&<div style={{fontSize:10,color:'#C6A585',fontWeight:600,marginTop:3}}>🔥 {profile.streak}</div>}
            </div>
          </div>
        </div>
        {/* Per-mode level mini-bars */}
        <div style={{display:'flex',gap:5}}>
          {MODE_DEFS.map(md=>{
            const lv=ml[md.id]||0;const on=content[md.id]?.on||md.id==='intervals';
            const{pct}=xpToNext(xpByMode?.[md.id]||0);
            const att=dailyAttempts?.[md.id]||0;const attDone=att>=MAX_ATT;
            return(<div key={md.id} style={{flex:1,opacity:on?1:.4}}>
              <div style={{fontSize:8,color:on?'#BEC9A6':'rgba(156,183,177,.5)',fontWeight:600,marginBottom:3,textAlign:'center',whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis'}}>{md.icon}</div>
              <div style={{height:3,background:'rgba(255,255,255,.1)',borderRadius:2,overflow:'hidden'}}><div style={{height:'100%',width:on?pct+'%':'0%',background:attDone?'#9CB7B1':'#C6A585',borderRadius:2}}/></div>
              <div style={{fontSize:8,color:on?'#9CB7B1':'rgba(156,183,177,.4)',marginTop:2,textAlign:'center'}}>{on?'Lv '+lv:'—'}</div>
            </div>);
          })}
        </div>
      </div>
      {/* Mode cards */}
      <div style={{padding:'16px 16px 0',display:'flex',flexDirection:'column',gap:10}}>
        {MODE_DEFS.map(md=>{
          const on=content[md.id]?.on||md.id==='intervals';
          const lv=ml[md.id]||0;
          const{pct,cur,need}=xpToNext(xpByMode?.[md.id]||0);
          const att=dailyAttempts?.[md.id]||0;const attDone=att>=MAX_ATT;
          return(<div key={md.id} onClick={()=>on&&onSelect('earTraining',md.id)}
            style={{background:'white',borderRadius:18,padding:'16px 18px',cursor:on?'pointer':'default',border:'1.5px solid '+(on?'transparent':'#BEC9A6'),boxShadow:on?'0 3px 16px rgba(64,81,71,.09)':undefined,opacity:on?1:.55,position:'relative',overflow:'hidden'}}>
            {on&&<div style={{position:'absolute',top:0,right:0,width:60,height:60,background:'#D1E1DD',borderRadius:'0 18px 0 60px',opacity:.4}}/>}
            <div style={{display:'flex',alignItems:'flex-start',justifyContent:'space-between',marginBottom:8}}>
              <div style={{display:'flex',alignItems:'center',gap:8}}>
                <span style={{fontSize:20}}>{md.icon}</span>
                <div>
                  <div style={{fontFamily:"'Fraunces',serif",fontSize:15,fontWeight:700,color:'#405147',lineHeight:1}}>{md.label}</div>
                  {on&&<div style={{fontSize:9,color:'#9CB7B1',marginTop:2}}>Level {lv}</div>}
                </div>
              </div>
              {on?(<div style={{display:'flex',alignItems:'center',gap:6}}>{attDone&&<span style={{fontSize:9,background:'#BEC9A6',color:'#405147',borderRadius:4,padding:'2px 6px',fontWeight:700}}>✓ Done</span>}<span style={{fontSize:11,color:'#405147',fontWeight:700}}>→</span></div>):(<span style={{fontSize:10,color:'#9CB7B1',background:'#F2EEE6',borderRadius:5,padding:'2px 7px'}}>{md.req}</span>)}
            </div>
            <div style={{fontSize:11,color:'#9CB7B1',lineHeight:1.5,marginBottom:on?10:0}}>{md.desc}</div>
            {on&&(<div style={{height:3,background:'#F2EEE6',borderRadius:2,overflow:'hidden'}}><div style={{height:'100%',width:pct+'%',background:attDone?'#BEC9A6':'#C6A585',borderRadius:2,transition:'width .5s'}}/></div>)}
            {on&&need>0&&<div style={{fontSize:9,color:'#BEC9A6',marginTop:3}}>{cur}/{need} xp to Level {lv+1}</div>}
          </div>);
        })}
        {/* Coming soon */}
        <div style={{background:'white',borderRadius:18,padding:'16px 18px',opacity:.45,border:'1.5px solid #BEC9A6',display:'flex',gap:10,alignItems:'center'}}>
          <span style={{fontSize:20,filter:'grayscale(1)'}}>📄</span>
          <div style={{flex:1}}><div style={{fontFamily:"'Fraunces',serif",fontSize:15,fontWeight:700,color:'#405147'}}>Reading</div><div style={{fontSize:11,color:'#9CB7B1',lineHeight:1.4,marginTop:2}}>Notation and sight-reading. Coming soon.</div></div>
          <span style={{fontSize:9,color:'#9CB7B1',background:'#F2EEE6',borderRadius:4,padding:'2px 7px',fontWeight:600}}>Soon</span>
        </div>
        <div style={{background:'white',borderRadius:18,padding:'16px 18px',opacity:.45,border:'1.5px solid #BEC9A6',display:'flex',gap:10,alignItems:'center'}}>
          <span style={{fontSize:20,filter:'grayscale(1)'}}>🎚</span>
          <div style={{flex:1}}><div style={{fontFamily:"'Fraunces',serif",fontSize:15,fontWeight:700,color:'#405147'}}>Audio Engineering</div><div style={{fontSize:11,color:'#9CB7B1',lineHeight:1.4,marginTop:2}}>Frequency, EQ, and dynamics by ear. Coming soon.</div></div>
          <span style={{fontSize:9,color:'#9CB7B1',background:'#F2EEE6',borderRadius:4,padding:'2px 7px',fontWeight:600}}>Soon</span>
        </div>
        {/* Leaderboard */}
        {Array.isArray(lb)&&lb.length>0&&(
          <div style={{background:'white',borderRadius:18,padding:'16px 18px',border:'1.5px solid #BEC9A6'}}>
            <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',marginBottom:10}}><div style={{fontFamily:"'Fraunces',serif",fontSize:15,fontWeight:700,color:'#405147'}}>Today's Board</div>{myRank>0&&<div style={{fontSize:10,color:'#9CB7B1'}}>You · #{myRank}</div>}</div>
            {lb.slice(0,5).map((e,i)=>(<div key={i} style={{display:'flex',alignItems:'center',gap:8,padding:'6px 0',borderBottom:i<4?'1px solid #BEC9A6':undefined}}><span style={{fontSize:12,fontWeight:700,color:i===0?'#c9a227':i===1?'#9CB7B1':i===2?'#C6A585':'#bbb',minWidth:18}}>{i===0?'🥇':i===1?'🥈':i===2?'🥉':'#'+(i+1)}</span><span style={{flex:1,fontSize:12,fontWeight:600,color:'#405147'}}>{e.name}</span><span style={{fontFamily:"'Fraunces',serif",fontSize:12,fontWeight:700,color:'#405147'}}>{(e.total||0).toLocaleString()}</span></div>))}
          </div>
        )}
        {/* Library link */}
        <div onClick={()=>onSelect('library')} style={{background:'transparent',borderRadius:14,padding:'12px 16px',cursor:'pointer',border:'1px solid #BEC9A6',display:'flex',alignItems:'center',gap:10,opacity:.7,marginBottom:8}}>
          <span style={{fontSize:18}}>📖</span>
          <div style={{flex:1}}><div style={{fontFamily:"'Fraunces',serif",fontSize:13,fontWeight:700,color:'#405147'}}>Music Library</div><div style={{fontSize:11,color:'#9CB7B1',marginTop:1}}>Reference guides for your unlocked content</div></div>
          <span style={{color:'#9CB7B1',fontSize:13}}>›</span>
        </div>
        <div style={{height:16}}/>
      </div>
    </div>
    {showGlobalStats&&<GlobalStatsSheet history={history||[]} lb={lb||[]} profile={profile} dailyScore={dailyScore} onClose={()=>setShowGlobalStats(false)}/>}
  );
}

const EMODES=[{id:'intervals',label:'Intervals',icon:'↔'},{id:'chords',label:'Chords',icon:'♪'},{id:'scales',label:'Scales',icon:'〜'},{id:'progressions',label:'Progs',icon:'♫'},{id:'tempo',label:'Tempo',icon:'♩'}];

function EarTraining({xpByMode,setXpByMode,profile,setProfile,dailyScore,setDailyScore,dailyAttempts,setDailyAttempts,initialMode,onBack,onScoreUpdate}){
  const[mode,setMode]          =useState(initialMode||'intervals');
  const[content,setContent]    =useState(()=>getContent(xpByMode));
  const[question,setQuestion]  =useState(null);
  const[selected,setSelected]  =useState(null);
  const[bounce,setBounce]      =useState(null);
  const[bounceKey,setBounceKey]=useState(0);
  const[tempoG,setTempoG]      =useState('');
  const[tempoDone,setTempoD]   =useState(false);
  const[round,setRound]        =useState(0);
  const[playing,setPlaying]    =useState(false);
  const[fillDur,setFillDur]    =useState(1800);
  const[revealed,setRevealed]  =useState(false);
  const[stats,setStats]        =useState({intervals:{f:0,s:0},chords:{f:0,s:0},scales:{f:0,s:0},progressions:{f:0,s:0},tempo:{f:0,s:0}});
  const[weights,setWeights]    =useState({});
  const[conf,setConf]          =useState({});
  const[history,setHistory]    =useState([]);
  const[lb,setLb]              =useState([]);
  const[lvUpQ,setLvUpQ]        =useState([]);
  const[showStats,setShowStats]=useState(false);
  const[showRoad,setShowRoad]  =useState(false);
  const[showIntro,setShowIntro]=useState(false);

  const playingR=useRef(false);
  const unlocked=useRef(false);
  const isFirstQ=useRef(true);
  const revealRef=useRef(null);
  const autoAdv=useRef(null);
  const prevLvsRef=useRef(Object.fromEntries(Object.keys(EMPTY_XPM()).map(m=>[m,levelFromXp(xpByMode?.[m]||0)])));
  const lvUpActiveRef=useRef(false);
  const pendingNextRef=useRef(false);

  const modeXp=xpByMode?.[mode]||0;
  const modeLv=levelFromXp(modeXp);
  const modeXpInfo=xpToNext(modeXp);
  const modeAtt=dailyAttempts?.[mode]||0;
  const modeExhausted=modeAtt>=MAX_ATT;
  const allExhausted=EMODES.filter(em=>content[em.id]?.on||em.id==='intervals').every(em=>(dailyAttempts?.[em.id]||0)>=MAX_ATT);

  // Load data
  useEffect(()=>{
    if(profile?.id){
      loadLB().then(b=>setLb(Array.isArray(b)?b:[])).catch(()=>{});
    }}
  ,[profile?.id]);

  // Show intro on first visit to a mode
  useEffect(()=>{
    if(profile&&!profile.seenModes?.[mode])setShowIntro(true);
    else setShowIntro(false);
  },[mode,profile?.id]);

  // Build question
  useEffect(()=>{
    if(showIntro)return;
    const cfg=content[mode];if(!cfg?.pool?.length&&mode!=='tempo')return;
    setQuestion(buildQ(mode,content,weights,conf));
    setSelected(null);setBounce(null);setTempoG('');setTempoD(false);setRevealed(false);
  },[round,mode,showIntro]);

  // Per-mode level-up detection
  useEffect(()=>{
    const newLv=levelFromXp(xpByMode?.[mode]||0);
    const prevLv=prevLvsRef.current[mode]||1;
    if(newLv>prevLv){
      const gained=(UNLOCKS_BY_MODE[mode]||[]).filter(u=>u.lv>prevLv&&u.lv<=newLv&&u.name);
      if(gained.length){
        lvUpActiveRef.current=true;
        setLvUpQ(q=>[...q,{level:newLv,unlocks:gained,modeName:MODE_LABELS[mode]?.label||mode}]);
      }
      prevLvsRef.current={...prevLvsRef.current,[mode]:newLv};
      setContent(getContent(xpByMode));
    }
  },[xpByMode,mode]);

  // Auto-play new question
  useEffect(()=>{
    if(!question||!unlocked.current)return;
    if(isFirstQ.current){isFirstQ.current=false;return;}
    if(lvUpActiveRef.current)return;
    const t=setTimeout(()=>doPlay(question,true),300);
    return()=>clearTimeout(t);
  },[question]);

  function scheduleReveal(dur){clearTimeout(revealRef.current);revealRef.current=setTimeout(()=>setRevealed(true),dur);}

  const doPlay=useCallback(async(q,autoplay=false)=>{
    if(!q||playingR.current)return;
    playingR.current=true;setPlaying(true);
    try{
      const ctx=getCtx();if(ctx.state==='suspended')await ctx.resume();
      unlocked.current=true;
      const dur=scheduleAudio(ctx,q);
      setFillDur(dur);
      if(!revealed)scheduleReveal(dur);
      setTimeout(()=>{playingR.current=false;setPlaying(false);},dur);
    }catch{playingR.current=false;setPlaying(false);}
  },[revealed]);

  const handleAnswer=useCallback((id)=>{
    if(selected!==null)return;
    clearTimeout(revealRef.current);clearTimeout(autoAdv.current);
    const cid=question.cid;const ok=String(id)===String(cid);
    setSelected(id);
    setStats(s=>({...s,[mode]:{...s[mode],s:s[mode].s+(ok?1:0),f:s[mode].f+(ok?0:1)}}));
    const newAtt={...dailyAttempts,[mode]:(dailyAttempts[mode]||0)+1};
    setDailyAttempts(newAtt);saveDailyAttempts(newAtt);
    const newStreak=ok?(profile.streak||0)+1:0;
    setWeights(w=>({...w,[mode]:wUpd(w[mode]||initW(content[mode].pool||[]),cid,ok)}));
    if(!ok)setConf(c=>{const nm={...c};if(!nm[mode])nm[mode]={};if(!nm[mode][String(id)])nm[mode][String(id)]={};nm[mode][String(id)][String(cid)]=(nm[mode][String(id)][String(cid)]||0)+1;return nm;});
    // XP + score only within daily attempt cap
    const attBefore=dailyAttempts[mode]||0;
    if(attBefore<MAX_ATT&&ok){
      const gain=question.type==='tempo'
        ?calcTempoXp(newStreak,Math.abs((parseInt(id)||0)-question.cid)/question.cid)
        :calcXp(newStreak);
      const newModeXp=(xpByMode[mode]||0)+gain;
      const newXpByMode={...xpByMode,[mode]:newModeXp};
      setXpByMode(newXpByMode);
      const newScore=dailyScore+gain;setDailyScore(newScore);saveDailyScore(newScore);
      const bonusTxt=newStreak>1?` +${newStreak} streak`:'';
      setBounce('+'+gain+bonusTxt);setBounceKey(k=>k+1);
      const np={...profile,xpByMode:newXpByMode,streak:newStreak};setProfile(np);saveProfile(np);
      submitLB(np,newScore).then(()=>onScoreUpdate?.());
      saveHistory(np.id,{date:toDay(),total:newScore});
    } else {
      const np={...profile,streak:newStreak};setProfile(np);saveProfile(np);
      if(ok){setBounce('✓');setBounceKey(k=>k+1);}else{setBounce('✗');setBounceKey(k=>k+1);}
    }
    try{const ctx=getCtx();ok?playOK(ctx):playNG(ctx);}catch{}
    autoAdv.current=setTimeout(()=>{
      if(lvUpActiveRef.current){pendingNextRef.current=true;}
      else handleNextInner();
    },700);
  },[selected,question,mode,content,xpByMode,dailyScore,dailyAttempts,profile,revealed]);

  function handleNextInner(){
    clearTimeout(autoAdv.current);
    setSelected(null);setBounce(null);setTempoG('');setTempoD(false);setRevealed(false);
    setRound(r=>r+1);
  }

  function switchMode(m){
    if(!content[m]?.on&&m!=='intervals')return;
    clearTimeout(autoAdv.current);clearTimeout(revealRef.current);
    isFirstQ.current=true;unlocked.current=false;
    setMode(m);setSelected(null);setBounce(null);setTempoG('');setTempoD(false);setRevealed(false);
    setRound(r=>r+1);
  }

  function markIntroSeen(){
    const np={...profile,seenModes:{...(profile.seenModes||{}),[mode]:true}};
    setProfile(np);saveProfile(np);setShowIntro(false);
  }

  function choiceLabel(id){
    if(mode==='intervals'){const iv=IV.find(x=>x.id===Number(id));return{name:iv?.name||id,abbr:iv?.abbr||''};}
    if(mode==='chords'){const ch=CH[id];return{name:ch?.name||id,abbr:ch?.abbr||''};}
    if(mode==='scales'){const sc=SC_BY[id];return{name:sc?.name||id,abbr:''};}
    if(mode==='progressions'){const pg=PG_BY[id];return{name:pg?.name||id,abbr:''};}
    return{name:id+' BPM',abbr:''};
  }

  const numChoices=question?.choices?.length||2;
  const modeLabel=EMODES.find(e=>e.id===mode);

  return(
    <><Styles/>
    <div className='r-root'>

      {/* ── Header ── */}
      <div className='r-hdr'>
        <div className='hdr-row1'>
          <button className='hdr-back' onClick={onBack}>← <span style={{fontSize:10}}>Hub</span></button>
          <div className='hdr-title'>{modeLabel?.icon} {modeLabel?.label}</div>
          <div className='hdr-actions'>
            <button className='hdr-icon-btn' onClick={()=>setShowRoad(true)} title='Roadmap'>📍</button>
            <button className='hdr-icon-btn' onClick={()=>setShowStats(true)} title='Stats'>📊</button>
          </div>
        </div>
        {/* Mode XP bar — always visible */}
        <div className='hdr-xp-row'>
          <span style={{fontFamily:"'Fraunces',serif",fontSize:12,fontWeight:700,color:'#C6A585',minWidth:38}}>Lv {modeLv}</span>
          <div className='hdr-bar-wrap'>
            <div className='hdr-bar-fill' style={{width:modeXpInfo.pct+'%'}}/>
          </div>
          <span className='hdr-xp-frac'>{modeXpInfo.lv<MAX_LV?modeXpInfo.cur+'/'+modeXpInfo.need+' xp':'Max'}</span>
        </div>
        {/* Streak + daily score — always visible */}
        <div className='hdr-meta-row'>
          <span className='hdr-streak'>{profile?.streak>0?'🔥 '+profile.streak+' streak':'— streak'}</span>
          <span className='hdr-score'>Today: {(dailyScore||0).toLocaleString()} pts</span>
        </div>
      </div>

      {/* ── Mode nav ── */}
      <div className='r-nav'>
        {EMODES.map(em=>{
          const on=em.id==='intervals'||content[em.id]?.on;
          const done=(dailyAttempts?.[em.id]||0)>=MAX_ATT;
          let cls='r-nav-btn';if(mode===em.id)cls+=' active';if(done)cls+=' done';if(!on)cls+=' locked';
          return(<button key={em.id} className={cls} onClick={()=>on&&switchMode(em.id)}>
            {em.icon} {em.label}{done?' ✓':''}
          </button>);
        })}
      </div>

      {/* ── Attempt bar ── */}
      {!modeExhausted&&(
        <div className='att-bar-wrap'>
          <div className='att-bar-track'><div className='att-bar-fill' style={{width:Math.round(modeAtt/MAX_ATT*100)+'%'}}/></div>
          <div style={{fontSize:8,color:'#9CB7B1',marginTop:2,textAlign:'right',paddingRight:16}}>{modeAtt}/{MAX_ATT} attempts</div>
        </div>
      )}

      {/* ── Scrollable content ── */}
      <div className='r-scroll'>

        {modeExhausted&&(
          <div className='done-banner'>
            <div style={{fontSize:28,marginBottom:8}}>✓</div>
            <div style={{fontFamily:"'Fraunces',serif",fontSize:16,fontWeight:700,color:'#405147',marginBottom:4}}>Session complete</div>
            <div style={{fontSize:12,color:'#9CB7B1',lineHeight:1.6}}>You have used your {MAX_ATT} {mode} attempts for today.{allExhausted?'':' Try another mode below.'}</div>
          </div>
        )}

        {!modeExhausted&&question&&(<>
          <div className='r-qcard'>
            {question.type==='interval'&&<Piano na={question.na} nb={question.nb} octs={question.oct}/>}
            {question.type==='interval'&&(<div className='notes-row'>
              <div className='npill npa'><div className='nnm'>{NOTES[question.na%12]}</div><div className='nsub'>Root</div></div>
              <span style={{fontSize:14,color:'#BEC9A6'}}>{question.dir==='desc'?'←':'→'}</span>
              <div className='npill npb'><div className='nnm'>{NOTES[question.nb%12]}</div><div className='nsub'>Target</div></div>
            </div>)}
            {question.type==='chord'&&<><span className='m-icon'>♪</span><div className='info-chip'>Random key · Chord quality</div></>}
            {question.type==='scale'&&<><span className='m-icon'>〜</span><div className='info-chip'>Random root · {question.dir==='desc'?'↓ Descending':'↑ Ascending'}</div></>}
            {question.type==='progression'&&<><span className='m-icon'>♫</span><div className='info-chip'>Random key · Progression</div></>}
            {question.type==='tempo'&&<><span className='m-icon'>♩</span><div className='info-chip'>Listen to the pulse · What is the BPM?</div></>}
            <button className={'play-btn'+(playing?' playing':'')} onClick={()=>doPlay(question)} disabled={playing}>
              {playing&&!revealed&&<div key={'pf'+round} className='play-fill' style={{animationName:'ri_playFill',animationDuration:fillDur+'ms',animationTimingFunction:'linear',animationFillMode:'forwards'}}/>}
              <span className='play-btn-inner'>
                {playing?<><div className='wave-bars'><div className='wave-bar wb1'/><div className='wave-bar wb2'/><div className='wave-bar wb3'/><div className='wave-bar wb4'/><div className='wave-bar wb5'/></div>{revealed?'Replaying…':'Listening…'}</>:<span>{unlocked.current?'↺ Replay':'▶ Play'}</span>}
              </span>
            </button>
          </div>

          {question.type!=='tempo'&&revealed&&question.choices&&(
            <div className='r-choices'>
              <div className='choices-lbl'>What is this?</div>
              {bounce&&<div key={bounceKey} className='bounce-msg' style={{color:bounce.startsWith('+')||bounce==='✓'?'#405147':'#C6A585'}}>{bounce}</div>}
              <div className='choices-grid' style={numChoices<=3?{gridTemplateColumns:'repeat(3,1fr)'}:{}}>
                {question.choices.map(ch=>{
                  const id=typeof ch==='object'?ch.id:ch;const lbl=choiceLabel(id);let cls='cbtn';
                  if(selected!==null){if(String(id)===String(question.cid))cls+=' correct';else if(String(id)===String(selected))cls+=' wrong';}
                  return(<button key={id} className={cls} onClick={()=>handleAnswer(id)} disabled={selected!==null}>{lbl.abbr&&<span className='cabbr'>{lbl.abbr}</span>}<span style={{fontSize:lbl.abbr?10:11}}>{lbl.name}</span></button>);
                })}
              </div>
              {selected!==null&&<button onClick={handleNextInner} style={{width:'100%',marginTop:10,padding:'10px',background:'transparent',border:'1.5px solid #BEC9A6',borderRadius:10,fontFamily:"'Work Sans',sans-serif",fontSize:12,fontWeight:600,color:'#405147',cursor:'pointer'}}>Next →</button>}
            </div>
          )}

          {question.type==='tempo'&&revealed&&(
            <div style={{padding:'0 16px'}}>
              {bounce&&<div key={bounceKey} className='bounce-msg' style={{color:bounce.startsWith('+')||bounce==='✓'?'#405147':'#C6A585'}}>{bounce}</div>}
              <div className='tempo-wrap'>
                <input type='number' className='tempo-in' value={tempoG} placeholder='BPM' min={30} max={300} disabled={tempoDone} onChange={e=>setTempoG(e.target.value)} onKeyDown={e=>{if(e.key==='Enter'&&!tempoDone&&tempoG){setTempoD(true);handleAnswer(parseInt(tempoG,10));}}}/>
                <button className='tempo-sub' disabled={!tempoG||tempoDone} onClick={()=>{if(tempoG&&!tempoDone){setTempoD(true);handleAnswer(parseInt(tempoG,10));}}}>Submit</button>
              </div>
              {tempoDone&&<div style={{textAlign:'center',marginTop:6,fontSize:11,color:'#9CB7B1'}}>You: <strong style={{color:'#405147'}}>{tempoG}</strong> · Actual: <strong style={{color:'#405147'}}>{question.cid}</strong></div>}
              {!tempoDone&&<div style={{fontSize:10,color:'#9CB7B1',textAlign:'center',marginTop:4,fontStyle:'italic'}}>Count the beats — feel the space between them.</div>}
              {tempoDone&&<button onClick={handleNextInner} style={{width:'100%',marginTop:10,padding:'10px',background:'transparent',border:'1.5px solid #BEC9A6',borderRadius:10,fontFamily:"'Work Sans',sans-serif",fontSize:12,fontWeight:600,color:'#405147',cursor:'pointer'}}>Next →</button>}
            </div>
          )}
        </>)}
      </div>{/* end r-scroll */}

      {showIntro&&<ExerciseModeIntro mode={mode} onBegin={markIntroSeen}/>}
      {lvUpQ.length>0&&<LevelUp data={lvUpQ[0]} onDone={()=>{
        setLvUpQ(q=>{const next=q.slice(1);
          if(next.length===0){lvUpActiveRef.current=false;
            if(pendingNextRef.current){pendingNextRef.current=false;setTimeout(()=>handleNextInner(),80);}
            else{setTimeout(()=>doPlay(question,true),300);}}
          return next;
        });
      }}/>}
      {showStats&&<ModeStatsSheet mode={mode} stats={stats} onClose={()=>setShowStats(false)}/>}
      {showRoad&&<RoadmapSheet mode={mode} currentLevel={modeLv} onClose={()=>setShowRoad(false)}/>}
    </div>
    </>
  );
}

export default function App(){
  const[screen,setScreen]        =useState('hub');
  const[initMode,setInitMode]    =useState('intervals');
  const[profile,setProfile]      =useState(null);
  const[xpByMode,setXpByMode]    =useState(EMPTY_XPM());
  const[dailyScore,setDailyScore]=useState(0);
  const[dailyAttempts,setDA]     =useState({intervals:0,chords:0,scales:0,progressions:0,tempo:0});
  const[lb,setLb]                =useState([]);
  const[history,setHistory]      =useState([]);
  const refreshLb=()=>loadLB().then(b=>setLb(Array.isArray(b)?b:[])).catch(()=>{});
  useEffect(()=>{
    (async()=>{
      const p=await loadProfile();
      setProfile(p);
      setXpByMode(p.xpByMode||EMPTY_XPM());
      const ds=await loadDailyScore();setDailyScore(ds||0);
      const da=await loadDailyAttempts();setDA(da);
      refreshLb();
      // load history at App level for Hub stats
      if(p?.id){
        loadHistory(p.id).then(h=>setHistory(Array.isArray(h)?h:[])).catch(()=>{});
      }
    })();
  },[]);
  useEffect(()=>{
    if(screen==='hub'){
      refreshLb();
      // refresh history when returning to hub
      if(profile?.id)loadHistory(profile.id).then(h=>setHistory(Array.isArray(h)?h:[])).catch(()=>{});
    }
  },[screen]);
  if(!profile)return(<><Styles/><div style={{background:'#405147',minHeight:'100dvh',display:'flex',alignItems:'center',justifyContent:'center'}}><div style={{fontFamily:"'Fraunces',serif",fontSize:18,color:'#9CB7B1',fontStyle:'italic'}}>Loading…</div></div></>);
  if(!profile.welcomed)return(<><Styles/><WelcomeScreen onDone={async(name)=>{const np={...profile,name:name||profile.name,welcomed:true};setProfile(np);await saveProfile(np);}}/></>);
  if(screen==='library')return(<><Styles/><LibraryScreen xpByMode={xpByMode} onBack={()=>setScreen('hub')}/></>);
  if(screen==='earTraining')return(
    <EarTraining
      xpByMode={xpByMode} setXpByMode={setXpByMode}
      profile={profile} setProfile={setProfile}
      dailyScore={dailyScore} setDailyScore={setDailyScore}
      dailyAttempts={dailyAttempts} setDailyAttempts={setDA}
      initialMode={initMode}
      onBack={()=>setScreen('hub')}
      onScoreUpdate={refreshLb}
    />
  );
  return(<><Styles/><SubjectHub xpByMode={xpByMode} profile={profile} lb={lb} history={history} dailyScore={dailyScore} dailyAttempts={dailyAttempts} onSelect={(s,m)=>{if(m)setInitMode(m);setScreen(s);}}/></>);
}

The intention needs to be as follows: the progression of the app FOLLOWS the players journey. It keeps them in constant evolving with the game. I think that's where Duo shines: each lesson and set of exercises is geared to remove the ambiguity of the next step. There's a limit to the amount of effort you're allowed to put in, but that effort is always towards a logical, engineered next step, guided by someone who knows the language. Exercises are a mixture of senses. Mastery is achieved in the first phase before the next, and progression is gradually layered. This is gonna be further down the line though. I think this current approach is good. But it feels like it's engineered for a weird crowd? 
- Who's it for? Beginners like my parents or advanced people looking to get more diligent practice like me?
- Really, it's turning the former into the latter. The idea is to add increasing complexity AND energy levels which allow for longer practice time as the habit develops

SKILL TREE
- Tow modes: skill mode, game mode
- Start with note identification 
- Skill mode has an ever expanding skill tree starting with notes. Needs to be this way to encourage curiosity, so that you can deepen the areas you're curious about. Unlocking something only displays directly adjacent nodes? Or maybe show the whole landscape 
- Completing lessons in skill mode unlocks them in game mode, when people press on the node they should be shown what they'll gain, 
- Choosing a skill locks them into a lesson plan (leaving has them restart), same with each individual lesson
- Energy is either used for lessons or games
- NO ENCOURAGING ADDICTION, mindfulness and curiosity have to be at the forefront
- Passing a lesson gets progressively more difficult. Could distinguish between lesson and exam things? Like exam nodes will just randomly shuffle exercises from the pre-req nodes whereas lesson nodes unlock new types of exercises? Don't really need exams honestly it doesn't make sense
- Before a graph display, can just do a simple list display with all the potential directions 

How should game mode work?
- Individual scores for each game (and high scores)
- Point multipliers for enabling options (eg up/down, 
- Fixed amount of time to get as many points as possible
- One free attempt then spend energy to try again 
- I don't like the idea of any timed trials. Too mindless? There's gotta be away to do them more mindfully 

For engineering:
- Instead of hardcoding progression, offloading to a file
- Make exercise templates 

Need to architect and plan out app before taking it to Claude. App is too slow and frustrating. Should also make the second, try hard app for diligent people 

Cool intro for introducing a note: Start with a whole note, grow a stem, animate fill in, then animate growing out the subdivisions
"Every note has a place and time. A tone and rhythm."

# 03-13-2026

Need to 1) dive deeper into obsession roots and issues 2) put restrictions on app dev 3)

# 03-14-2026

So fucking anxious right now attention is constantly divided trying to people please this camping trip into existence obsession over the app anxiety and all I want to do is suppress sugar caffeine whatever it takes and every opportunity I get come back to it I can't be present I can't be here I have to get back appease the obsession fight the pain by indulging in it and then instead of having the capacity to be present and do my job all I actually end up fucking doing is degenerate sitting on my phone and I haven't ran I haven't meditated I haven't walked my dog I've just been stuck in an anxious trance and I'm terrified about nana and life is fleeting and I'm so stressed about all these next steps and I haven't been to the run club or jazz jam in a fucking month and it's wearing on me how much I'm surrounded by ineffective and unambitious people who are making it harder and harder to want to wake up early and run and all this shit because they don't fucking care

# 03-15-2026

I still feel anxious and unmotivated today. Like I'm going through the motions to prepare for the week, but I don't actually want any of it. I don't want to accomplish anything. Or practice anything. Or exercise. Or eat. Part of the problem is I haven't really ate since breakfast. But I feel numb and kind of hopeless. It feels pointless to try. I don't know what I want or where I'm going. And I don't really understand why I stopped masturbating now, even when on a deeper level it's made life so much better. I just see beautiful women and it makes me feel so horny

I did it anyways! I went shopping. I won't cook tonight, but I at least did this for myself

What am I trying to solve by improving music, teaching, and diet at once?
- Nanas death invariably comes to mind

I need a plan for working through these. I see that the major change in my life is that it's not just about improving money/business anymore, now it's about improving life and everything around it. But I need to decide on a good pacing.

What about 1 book at a time? Cycle subjects? 

What's the intentions for tomorrow?
Need to:
- Exrcise
- Meditate
- Practice
- Cook
- Clean basement

- Work 430-1130
- Break 1130-1230
- Walk Mu 1230-1315
- Meditate 1315-1400
- Practice 1400-1600
- Exercise 1600-1700
- Cook 1700+

