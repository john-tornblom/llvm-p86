program NestedFunctionTest1;
const
   s = 'OK';
   
var
   i,g : integer;
     
procedure level1;
   procedure level2;
      procedure level3;
      begin
	 g := 3;
	 i := 3;
      end; { level3 }
   begin
      g := 2;
      level3;
      i := 2;
   end; { level2 }
begin
   g := 1;
   level2;
   i := 1;
end; { level1 }

begin
   g := 0;
   i := 0;
   level1;
   
   if g = 3 then
      writeln(s)
   else
      halt(1);

   if i = 1 then
      writeln(s)
   else
      halt(1);
end.