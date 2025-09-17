# import asyncio
# from database.core import create_tables, check_user, get_tasks, get_leaders

# if __name__ == "__main__":
#     asyncio.run(create_tables())
#     # asyncio.run(get_tasks())
#     # asyncio.run(get_leaders())
#     pass



class Integer:
    

    @classmethod
    def verify_coord(cls, coord):
        if type(coord) != int:
            raise TypeError(f"Координата {coord} не верного параметра")
        
    def __set_name__(self, owner, name):
        self.name = "_" + name
    
    def __get__(self, instance, owner):
        return instance.__dict__[self.name]
    
    def __set__(self, instance, value):
        self.verify_coord(value)
        print(f"__set__: {self.name} = {value}")
        instance.__dict__[self.name] = value

class Point:
    x = Integer()
    y = Integer()

    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(2,2)
print(p.__dict__)
    

