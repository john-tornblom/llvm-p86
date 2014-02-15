PROGRAM RealCalculationTests2;
VAR
   r  : REAL;
   lr : LONGREAL;
   tr : TEMPREAL;
BEGIN
   r := 1.0 + 1.0;
   if r = 2 then
      writeln('OK')
   else
      halt(1);
   
   r := 1.0 - 1.0;
   if r = 0 then
      writeln('OK')
   else
      halt(1); 
   
   r := 4.0 * 4.0;
   if r = 16 then
      writeln('OK')
   else
      halt(1);
   
   r := 4.0 / 2.0;
   if r = 2 then
      writeln('OK')
   else
      halt(1);



   lr := 1.0 + 1.0;
   if lr = 2 then
      writeln('OK')
   else
      halt(1);
   
   lr := 1.0 - 1.0;
   if lr = 0 then
      writeln('OK')
   else
      halt(1); 
   
   lr := 4.0 * 4.0;
   if lr = 16 then
      writeln('OK')
   else
      halt(1);
   
   lr := 4.0 / 2.0;
   if lr = 2 then
      writeln('OK')
   else
      halt(1);

   
   tr := 1.0 + 1.0;
   if tr = 2 then
      writeln('OK')
   else
      halt(1);
   
   tr := 1.0 - 1.0;
   if tr = 0 then
      writeln('OK')
   else
      halt(1); 
   
   tr := 4.0 * 4.0;
   if tr = 16 then
      writeln('OK')
   else
      halt(1);
   
   tr := 4.0 / 2.0;
   if tr = 2 then
      writeln('OK')
   else
      halt(1);

end.
