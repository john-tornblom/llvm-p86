PROGRAM ScopeTest;
VAR
   i : INTEGER;
BEGIN
   i := 1;

BEGIN
   i := i + 1;
END;

   i := i + 1;

   if i = 3 then
      writeln("OK")
   else
      halt(1);

END.