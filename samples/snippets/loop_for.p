program ForLoopTest;
var
   a : INTEGER;
   i : INTEGER;
   j : INTEGER;
begin
   a := 0;
   for i := 1 to 10 do
   begin
      a := a + 1;
   end;

   if a = 10 then
      writeln("OK")
   else
      halt(1);

   a := 0;
   for i := 1 to 20 do
      if i < 11 then
	 a := a + 1;

   if a = 10 then
      writeln("OK")
   else
      halt(1);

   a := 0;
   for i := 10 downto 1 do
   begin
      a := a + 1;
   end;
   

   if a = 10 then
      writeln("OK")
   else
      halt(1);


   a := 0;
   for i := 1 to 10 do
      for j := 1 to 10 do
	 a := a + 1;

   if a = 100 then
      writeln("OK")
   else
      halt(1);

end.
