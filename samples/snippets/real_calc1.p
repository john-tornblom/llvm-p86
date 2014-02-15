PROGRAM RealCalculationTests1;
VAR
   r  : REAL;
   lr : LONGREAL;
   tr : TEMPREAL;
BEGIN
   r := 0;

   if r = 0 then
      writeln('OK')
   else
      halt(1);

   r := 1 + 1;
   if r = 2 then
      writeln('OK')
   else
      halt(1);
   
   r := 1 - 1;
   if r = 0 then
      writeln('OK')
   else
      halt(1); 
   
   r := 4 * 4;
   if r = 16 then
      writeln('OK')
   else
      halt(1);
   
   r := 4 / 2;
   if r = 2 then
      writeln('OK')
   else
      halt(1);

   r := 4 / 3;
   if r > 1 then
      writeln('OK')
   else
      halt(1);
   
   r := 15 mod 4;
   if r = 3 then
      writeln('OK')
   else
      halt(1);

   lr := 0;

   if lr = 0 then
      writeln('OK')
   else
      halt(1);

   lr := 1 + 1;
   if lr = 2 then
      writeln('OK')
   else
      halt(1);
   
   lr := 1 - 1;
   if lr = 0 then
      writeln('OK')
   else
      halt(1); 
   
   lr := 4 * 4;
   if lr = 16 then
      writeln('OK')
   else
      halt(1);
   
   lr := 4 / 2;
   if lr = 2 then
      writeln('OK')
   else
      halt(1);

   lr := 4 / 3;
   if lr > 1 then
      writeln('OK')
   else
      halt(1);
   
   lr := 15 mod 4;
   if lr = 3 then
      writeln('OK')
   else
      halt(1);



   tr := 0;

   if tr = 0 then
      writeln('OK')
   else
      halt(1);

   tr := 1 + 1;
   if tr = 2 then
      writeln('OK')
   else
      halt(1);
   
   tr := 1 - 1;
   if tr = 0 then
      writeln('OK')
   else
      halt(1); 
   
   tr := 4 * 4;
   if tr = 16 then
      writeln('OK')
   else
      halt(1);
   
   tr := 4 / 2;
   if tr = 2 then
      writeln('OK')
   else
      halt(1);

   tr := 4 / 3;
   if tr > 1 then
      writeln('OK')
   else
      halt(1);

   tr := 15 mod 4;
   if tr = 3 then
      writeln('OK')
   else
      halt(1);

END.

   