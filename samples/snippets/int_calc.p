PROGRAM IntCalculationTests;
VAR
   i : INTEGER;
   
BEGIN
   i := 1 + 1;
   if i = 2 then
      writeln("OK")
   else
      halt(1);
   
   i := 1 - 1;
   if i = 0 then
      writeln("OK")
   else
      halt(1); 
   
   i := 4 * 4;
   if i = 16 then
      writeln("OK")
   else
      halt(1);
   
   i := 4 div 3;
   if i = 1 then
      writeln("OK")
   else
      halt(1);
   
   i := 15 mod 4;
   if i = 3 then
      writeln("OK")
   else
      halt(1);
END.