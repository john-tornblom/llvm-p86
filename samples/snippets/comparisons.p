program Comparisons;
var
   a : INTEGER;
   i : INTEGER;
begin
   a := 1;
   if (a = 1) and (a = 2) and (a = 3) then
      halt(1)
   else
      writeln("OK");
	
 
   a := 0;
   for i := 1 to 10 do
      a := a + 1;
		
   if a = 10 then
      writeln("OK")
   else
      halt(1);

   a := 0;
   i := 10;
   while i > 1 do
   begin
      a := a + 1;
      i := i - 1;
   end;

   if a = 9 then
      writeln("OK")
   else
      halt(1);

   a := 0;
   i := 1;
   repeat
   begin
      a := a + 1;
      i := i + 1;
   end until i = 10;

   if a = 9 then
      writeln("OK")
   else
      halt(1);
end.
