PROGRAM RealCalculationTests3;
VAR
   r  : REAL;
   lr : LONGREAL;
BEGIN
   r := 1 + 1.0;
   if r = 2 then
      writeln("OK")
   else
      halt(1);
   
   r := 1 - 1.0;
   if r = 0 then
      writeln("OK")
   else
      halt(1); 
   
   r := 4 * 4.0;
   if r = 16 then
      writeln("OK")
   else
      halt(1);
   
   r := 4 / 2.0;
   if r = 2 then
      writeln("OK")
   else
      halt(1);

  lr := 1 + 1.0;
   if lr = 2 then
      writeln("OK")
   else
      halt(1);
   
   lr := 1 - 1.0;
   if lr = 0 then
      writeln("OK")
   else
      halt(1); 
   
   lr := 4 * 4.0;
   if lr = 16 then
      writeln("OK")
   else
      halt(1);
   
   lr := 4 / 2.0;
   if lr = 2 then
      writeln("OK")
   else
      halt(1);
end.
