program IfElseTest;

const
   s = 'OK';
var
   i : integer;
BEGIN
   i := 1;

   if i = 1 then
      writeln(s)
   else
      halt(1);
   
   if i <> 1 then
      halt(1)
   else
      writeln(s);

   if i = 0 then
      halt(1)
   else if i = 2 then
      halt(1)
   else
      writeln(s);

   if i = 2 then
      halt(1)
   else if i = 1 then
      writeln(s)
   else
      halt(1);
   
   if i = 1 then
      writeln(s)
   else if i = 2 then
      halt(1)
   else
      halt(1);

   if i = 1 then
   begin
      i := i + 1;
      i := i + 1;
      writeln(s);
   end;

   if i <> 3 then
      halt(1)
   else
      writeln(s);
END.