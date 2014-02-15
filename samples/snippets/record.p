program recordTest;

type
   T_OBJ =  record
	       attr : integer;
	    end;

   T_OBJ1 =  record
		obj : T_OBJ;
	    end;    

   T_OBJ0 =  record
		obj1 : T_OBJ1;
	    end;     
   
   T_DATE = record
	       val   : integer;
	       day   : array[0..1] of integer;
	       month : array[0..1] of T_OBJ;
	       year  : array[0..4] of integer;
	    end;     
   T_TEST = record
	       date : array[0..10] of T_DATE;
	       cnt  : integer;
	       rec  : record
			 a : integer;
			 b : integer;
		      end;
	    end;	   
var	 
   today : T_DATE;
   i	 : integer;
   test	 : T_TEST;
   obj0	 : T_OBJ0;
   
begin
   today.day[0] := 1;
   i:= today.day[0];
   
   if i = 1 then
      writeln('OK')
   else
      halt(1);
   
   if today.day[0] = 1 then
      writeln('OK')
   else
      halt(1);
   
   test.date[2].month[1].attr := 213;
   test.cnt := 1;
   test.date[5].val := 24;

   if test.cnt = 1 then
      writeln('OK')
   else
      halt(1);

   if test.date[5].val = 24 then
      writeln('OK')
   else
      halt(1);

   if test.date[2].month[1].attr = 213 then
      writeln('OK')
   else
      halt(1);



   obj0.obj1.obj.attr := 5;

   if obj0.obj1.obj.attr = 5 then
      writeln('OK')
   else
      halt(1);
end.
