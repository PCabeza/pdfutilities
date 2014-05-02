#include <cstring>
#include <cstdlib>

#include <fstream>
#include <iostream>
#include <stack>
#include <map>
#include <limits>

using std::stack;
using std::cout;
using std::ifstream;
using std::ios;
using std::numeric_limits;

void* mempbrk(void* mem, const char* str, size_t size){
    for(char* i=(char*)mem; i != (char*)mem+size ;++i){
	if(*i!=0 && strchr(str,*i)!=NULL) return i;
    }
    return NULL;
}



unsigned near_upper_2(unsigned num){
    for(int i=0 ; i<numeric_limits<unsigned>::digits ; i++)
	if( (1<<i) >= num ) return 1<<(i);
    return 1<<numeric_limits<unsigned>::digits-1;
}


// Todo undefined for size=0
struct object_t {
    explicit object_t(size_t size=0):_contents(size==0?NULL:
					       new char[near_upper_2(size)]),
				     _size(0),
				     _capacity(near_upper_2(size)){}
    object_t(void* mem,size_t size) :object_t(size){
	memcpy((void*)_contents,mem,size);
	_size=size;
    }

    void append(void* mem, size_t size){
	if(size+_size > _capacity){
	    _capacity=near_upper_2(size+_size);
	    char* newcontent=new char[_capacity];

	    memcpy(newcontent,_contents,_size);
	    delete[] _contents;
	    _contents=newcontent;
	}
	memcpy(_contents+_size,mem,size);
	_size+=size;
    }

    virtual ~object_t(){
	delete[] _contents;
    }

    char* _contents;
    size_t _size;
    size_t _capacity;
};




enum { SIZE=10*1024 }; // 10K buffer size
const char* WHITES=" \n\t\r";

typedef std::pair<int,int> obkey_t;
typedef std::pair<obkey_t,char*> stack_t;
typedef std::map<obkey_t,object_t> object_map;



int main(int argc,char* argv[]){

    ifstream file("indi.pdf",ios::in);    
    stack<stack_t> op_stack;
    char buffer[SIZE],*a_ptr=buffer,*o_ptr,
	*f_num,*s_num;

    file.read(buffer,SIZE);
    
    do{
    	o_ptr=(char*)mempbrk((void*) a_ptr,WHITES,SIZE-(a_ptr-buffer));
    	if(o_ptr==NULL){
    	    break;
    	}

    	if(strncmp(a_ptr,"obj",o_ptr-a_ptr)==0){
    	    cout << "Found obj!\n";
    	    atoi(f_num);
    	    atoi(s_num);
    	    op_stack.push(stack_t( obkey_t(atoi(f_num),atoi(s_num)),
    				   a_ptr));
    	}
    	else if(strncmp(a_ptr,"endobj",o_ptr-a_ptr)==0){
    	    cout << "Found endobj!\n\n";
    	    cout << "Key is: " << op_stack.top().first.first << ' '
    		 << op_stack.top().first.second << '\n';
		
    	    cout.write(op_stack.top().second,o_ptr-op_stack.top().second);
    	    cout << "\n\n";
    	    op_stack.pop();
    	}
    	f_num=s_num;
    	s_num=a_ptr;
    	a_ptr=o_ptr+strspn(o_ptr,WHITES);
    	while(a_ptr==NULL && a_ptr-buffer!=SIZE) ++a_ptr;
    }while(a_ptr!=NULL);
    
    return 0;
}
