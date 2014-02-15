program ParamsTest;

var
   x : real;
   y : real;
   
function sum(a : real; b:integer; c:integer; d:real) : real;
begin
   sum := a + b + c + d;
end;

begin
   x := sum(sum(sum(1.0, 2, 3, 4.0), 5, 6, 7.0), 8, 9, 10.0);
   y := x - 55.0;
   
   if y = 0 then
      writeln("OK")
   else
      halt(1);
end.

