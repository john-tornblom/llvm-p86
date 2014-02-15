program LogicTest;

const
   s = 'OK';
   
var
   a : INTEGER;
   r : REAL;
begin
   r := 1.0;
   a := 1;
   
   { not equal operator test }
   if a <> 0 then
      writeln(s);
   if a <> 1 then
      halt(1);
   if r <> 1.1 then
      writeln(s);
   if r <> 1.0 then
      halt(1);

   { equal operator test }
   if a = 0 then
      halt(1);
   if a = 1 then
      writeln(s);
   if r = 1.1 then
      halt(1);
   if r = 1.0 then
      writeln(s);

   { less than operator test }
   if a < 0 then
      halt(1);
   if a < 1 then
      halt(1);
   if a < 2 then
      writeln(s);
   if r < 1.1 then
      writeln(s);
   if r < 1.0 then
      halt(1);
   if r < 0 then
      halt(1);

    { less than or equal operator test }
   if a <= 0 then
      halt(1);
   if a <= 2 then
      writeln(s);
   if a <= 1 then
      writeln(s);
   if r <= 1.1 then
      writeln(s);
   if r <= 1.0 then
      writeln(s);
   if r <= 0.9 then
      halt(1);


   { greather than operator test }
   if a > 0 then
      writeln(s);
   if a > 1 then
      halt(1);
   if a > 2 then
      halt(1);
   if r > 1.1 then
      halt(1);
   if r > 1.0 then
      halt(1);
   if r > 0.0 then
      writeln(s);


   { greather than or equal operator test }
   if a >= 0 then
      writeln(s);
   if a >= 2 then
      halt(1);
   if a >= 1 then
      writeln(s);
   if r >= 1.1 then
      halt(1);
   if r >= 1.0 then
      writeln(s);
   if r >= 0.9 then
      writeln(s);

   { NOT operator test }
   if not a = 0 then
      writeln(s);
   if not a = 1 then
      halt(1);
end.
