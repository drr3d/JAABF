########################################################################
# SMT pada grammar saya buat sebagai singkatan dari
#       => likely a SiMilar Token
# dimaksudkan jika suatu token masuk kedalam SMT, token-token tersebut
# memiliki kemungkinan membentuk suatu entitas atau makna tersendiri
# Ataupun bisa bertransformasi bentuk tag nya tergantung jenis kata yang
# mengawali dan mengakhiri
########################################################################

# Perlu diperhatikan, aturan peletakan chunk juga berpengaruh
# chuk parser akan memproses dari yang paling atas dahulu
chunk_grammar_pan = r"""
  TIME: {<IN|IO|NUM>?<TIME>}
         {<TIME>?<NUM>?<TIME>}
  UNIT: {<IN>?<NUM><NNC|NN>}
        }<IN>{
  DATE: {<NUM><MONTH>}
  PREP: {<IN|IO><IN|IO>}
        {<IN|IO><JJ>?<NP>?}#PREP = Preposisi = kata depan
        }<IN|IO>{
        }<NP>{
        {<PRP>}
  TP: {<WP>}
  KP: {<KSUB><ADV>}        #KSUB = kata penghubung/conjunction
  NP: {<NNC><NN>}
      {<DT>?<NN>+<NNC>?<NUM>?}
      {<NN|NNP|NNU|NNC><ADJ|VBI>}
      {<NN|NNP|NNU|NNC><NN|NNP|NNU|NNC|NP><KKORD>?<NN|NNC>?}
      {<NN|NNP|NNU|NNC><NN|NNP|NNU|NNC|NP><NN|NNC>?}
      {<PREP>?<NN|NNP|NNU|NNC><NN|NNP|NNU|NNC|NP>}
      }<PREP>{
  VP: {<VBT|VBI|VB>+}
      {<RB><NP>}
  SMT1: {<NN|NNP|NNU><NN|NNP|NNU>+}
        {<NN|NNP|NNU><NP>}
  SMT2: {<XX>+}
  SMT3: {<NNC><NNC|NN|MISC>+}
  SMT4: {<F-MISC><S-MISC><T-MISC>?<G-MISC>?<L-MISC>?}
        {<MISC>+}
  SMT5: {<SC><JJ><VBI|VBT>}
        }<VBI|VBT>{
  
  INTENT: {<VP|VBI|VBT><NP><PRON>?<NNC|NN>?}
          {<PRED><PRON>?<NNC|NN>?}
          {<CC><VP>}
  PERSON: {<PER>}
          {<F-PER><S-PER><T-PER>?<G-PER>?}
  COUNTRY: {<NP|NN>?<LOC><DIRC>}
           }<NP|NN>{
  LOC: {<PREP><F-LOC|LOC>}
       }<PREP>{
       {<PREP><F-LOC><S-LOC><T-LOC>?<G-LOC>?}
       }<PREP>{
       {<PREP><NP>}
       }<PREP>{
       {<PREP><NN><MISC><LOC>?}
       }<PREP>{
       {<PREP><NN>?<VBT>?<F-LOC|LOC>}
       }<PREP>{
       {<IN><NN|NNC><NP>}
       {<IN|IO><IN|IO><NN><NNC>}
       {<IN|IO><IN|IO><NNC|NN><SC><RB><JJ>}
       {<F-LOC><S-LOC><T-LOC>?<G-LOC>?<DIRC>?<LOC>?}
       {<IN|IO><NN|NNC>+<DT>?}
       }<IN|IO>{
       {<IN|IO><NN>?<VBT>?<F-LOC|LOC>}
       }<IN|IO>{
       {<IN|IO><NN><NN|NNC><LOC>}
       }<IN|IO>{
       {<NNC><DT>}
       {<IN|IO><F-DIRC><S-DIRC>}
       }<IN|IO>{
       {<IN|IO><DIRC><NNC>}
       }<IN|IO>{
       {<IN|IO><NN><DIRC><LOC>}
       }<IN|IO>{
       {<IN|IO><NN><MISC><LOC>?}
       }<IN|IO>{
       {<IN|IO><NP><K-TEMPAT>}
       }<NP>{
       }<K-TEMPAT>{
       }<IN|IO>{
       {<IN|IO><NN|NP><CTRY>}
       }<IN|IO>{
       {<CTRY>}
       {<K-TEMPAT><PREP|SC|CC|NP>?<K-TEMPAT>?<COUNTRY>?<DIRC>?}
       {<CITY_ORIGIN>}
       {<CITY_DESTINATION>}
  ORG: {<F-ORG><S-ORG><T-ORG>?<G-ORG>?<L-ORG>?}
       {<ORG>}
       {<DT><NNC><NN|NP><LOC>}
       }<DT>{
       }<LOC>{
  K-TEMPAT: {<PREP|IN|IO><NP>+<PREP>?}
            {<PREP><LOC>}
            {<IN|IO><LOC>}
            
  SBJ: {<NP|CC|PREP|PRP>?<PRP|NN|NNP|NNU|NP|XX|SMT2|ORG|PERSON><PREP>?<PRED>}
       }<PRED>{
       }<PREP>{
  OBJ: {<PRED><NN|VP|NP|MISC|ORG|PERSON>+<K-TEMPAT>?<CC|PREP>?<K-TEMPAT>?<LOC>?<ORG>?}
       }<PRED>{
       {<PRED><SC>?<K-TEMPAT><CC|PREP>?<K-TEMPAT>?<LOC>?}
       }<PRED>{
       }<SC>{
  PRED: {<PREP>?<ADV|PREP><VBI|VBT|VB>}
        }<PREP>{
        {<VBT|VBI|VP><KKORD>?<IN>?<VP>?}
        {<KP><NP>}
        {<SMT1><ADJ>}
        }<SMT1>{
        {<VBT><SMT1>}
        }<SMT1>{
        {<VBT><NP>}
        }<NP>{
        {<PREP><ADJ>}
        }<PRPE>{
        {<KP><ADJ>}
        {<PREP><ADV><ADJ>}
        {<ADV><ADV><ADJ>}
        {<ADV>?<VPASIF>}
"""

chunk_grammar = r"""
  PREP: {<PREP><PREP>}     #PREP = Preposisi = kata depan
  TP: {<WP>}
  KP: {<KSUB><ADV>}        #KSUB = kata penghubung/conjunction
  NP: {<N><ADJ|VBI>}
      {<N><N><KKORD><N>}
      {<PREP>?<N><N>}
      }<PREP>{
      {<NUM><N>}
      #{<KP><ADJ>}
  VP: {<KP><VBT|VBI|V>}
      {<V><VBT>}
  SMT1: {<N><N>+}
        {<N><NP>}
  SMT2: {<XX>+}
  SMT3: {<PREP><N>}
  SMT4: {<SMT4>}
  SMT5: {<ADJ><NP|N>}
  SMT6: {<KKORD><XX>+}
  SMT7: {<N><XX>}
        {<XX><N>}
  SMT8: {<NP><N>}
  KET: {<PREP><NP|SMT8>}
       {<PREP><GOL><ADJ>}
  SBJ: {<NP>?<PRON|N|NP|XX|SMT2><PRED>}
       }<PRED>{
  SBJP: {<NP|N><KET><VPASIF|PRED>}
        }<VPASIF|PRED>{
        {<NP|N><VPASIF|PRED>}
        }<VPASIF|PRED>{
  OBJ: {<PRED><N|V|NP>}
       }<PRED>{
  PENJ: {<PREP><ADV|VBI>+}
        {<PREP><SMT5>}
  PRED: {<ADV|PREP><VBI|VBT|V>}
        {<VBT>+}
        {<KP><NP>}
        {<SMT1><ADJ>}
        }<SMT1>{
        {<VBT><SMT1>}
        }<SMT1>{
        {<VBT><NP>}
        }<NP>{
        {<PRON><ADJ>}
        }<PRON>{
        {<KP><ADJ>}
        {<PREP><ADV><ADJ>}
        {<ADV><ADV><ADJ>}
        {<ADV>?<VPASIF>}
"""
