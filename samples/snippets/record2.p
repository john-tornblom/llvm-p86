program record2Test;

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
var	 
   obj0	 : T_OBJ0;
   
begin
   obj0.obj1.obj.attr := 5;

   if obj0.obj1.obj.attr = 5 then
      writeln('OK')
   else
      halt(1);
end.