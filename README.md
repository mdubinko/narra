# narra
Long-form text-to-speech with fatigue-reducing dynamics

The front-half of this project is analyzing lots of audio data from available sources like librivox and
Mozilla Common Voice, to establish a dataset of significance about pitch, pace, and volume of spoken words,
and correlate that with as many things as possible--parts of speech, named entity recogniton, importance
of particular words and phrases (perhaps identified by natural language summarization).

The scratch\ directory has a short sample and some work-in-progress 
to capture these data.

Once a dataset large and accurate enough is assembled, then the back-half of this project is to take a
long-form piece of text, such as a novel, as input, and render it to Speech Synthesis Markup Language
(SSML) to include all the pauses and speech variations that breathe life into the text.

Ideally, I'd be able to feed one of my novels into this process and get a commercially acceptable result.