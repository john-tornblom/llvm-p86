program NestedFunctionTest2;
const
   s = 'OK';
   
var
   i, g : integer;

procedure level1(n, m : integer);
const
   PI =  3.14;
var
   r : real;
   procedure level2; 
      procedure level3;
      begin
	 n := 3;
	 m := 3;
	 r := PI;
      end; { level3 }
   begin
      n := 2;
      level3;
      if r = PI then
	 writeln(s)
      else
	 halt(1);
      m := 2;
   end; { level2 }
begin
   r := 0;
   n := 1;
   level2;
   m := 1;

   g := n;
   i := m;
end; { level1 }

begin
   g := 0;
   i := 0;
   level1(0, 0);

   if g = 3 then
      writeln(s)
   else
      halt(1);

   if i = 1 then
      writeln(s)
   else
      halt(1);
end.