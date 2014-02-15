program RepeatLoopTest;
var
   a : INTEGER;
   i : INTEGER;
begin
   a := 10;
   i := 1;
   
   repeat
      i := i + 1
   until i = a;

   if i = 10 then
      writeln("OK")
   else
      halt(1);

end.
