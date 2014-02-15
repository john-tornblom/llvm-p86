program WhileLoopTest;
var
   a : INTEGER;
   i : INTEGER;
begin
   a := 0;
   i := 10;
   while i >= 1 do
   begin
      a := a + 1;
      i := i - 1;
   end;

   if a = 10 then
      writeln("OK")
   else
      halt(1);


   a := 0;
   while a < 10 do
      if a < 20 then
	 a := a + 1;
   
   if a = 10 then
      writeln("OK")
   else
      halt(1);

end.
