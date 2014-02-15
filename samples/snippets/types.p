PROGRAM types;
VAR
   i : REAL;
BEGIN
	i := 3.2;
	i := 1.0 + i;

   if i = 4.2 then
      writeln('OK')
   else
      halt(1);
END.
