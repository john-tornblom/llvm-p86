program SimpleArrayTest;

var
   arr : array[0..10, 0..10] of integer;
   i   : integer;
   j   : integer;
begin
   arr[5][2] := 1;
   i := arr[5][2];

   arr[4,2] := 2;
   j := arr[4,2];
   
   if i = 1 then
      writeln("OK")
   else
      halt(1);
      
   if j = 2 then
      writeln("OK")
   else
      halt(1);

end.