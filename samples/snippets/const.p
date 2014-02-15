program ConstTest;

const
   tcnst    = 768;
   scst	    = 'this is a string';
   ccst	    = 'v';
   tsncst   = -52;
   rcnst    = 43.33;
   rscst    = -84.22;
   tsncst2  = -tcnst;
   tsncst3  = -tsncst;
   rscst2   = -rcnst;
   rscst3   = -rscst;
   testfile = true;
   mmaxint  = -maxint;
   
   NUM1	    = (5 + 3.14) * 3;
   NUM2	    = 4 div 1;
   NUM3	    = -3 + 5;
   num4	    = +num1 + num2;
   num5	    = -4;
   num6	    = -num5 + 1;
begin

   if num1 = +24.42 then
      writeln("OK")
   else
      halt(1);
   
   if num2 = 4 then
      writeln("OK")
   else
      halt(1);

   if num3 = 2 then
      writeln("OK")
   else
      halt(1);

 
   if num4 = 28.42 then
      writeln("OK")
   else
      halt(1);
   

   if num5 = -4 then
      writeln("OK")
   else
      halt(1);

  if num6 = 5 then
      writeln("OK")
   else
      halt(1);
end.