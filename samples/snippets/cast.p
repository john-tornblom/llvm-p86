PROGRAM cast;
VAR
   r : REAL;
   i : INTEGER;
BEGIN
   r := 3.14;
   i := 2;
   
   r := r + i;
   
   if (r > 5.139999) and (r < 5.1400001) then
      writeln('OK')
   else
      halt(1);
END.