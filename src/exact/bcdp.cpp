#include <algorithm>
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <bitset>
#include <vector>
#include <limits>
#include <random>
#include <queue>
#include <set>
using namespace std;

#include "Timer.h"

#ifdef _MSC_VER
#define COMPILER_RECOGNIZED
typedef unsigned __int8 CharName;
#endif
#ifdef __GNUC__
#define COMPILER_RECOGNIZED
typedef uint8_t CharName;
#endif
#ifndef COMPILER_RECOGNIZED
#error Did not recognize your compiler. Fix the above typedefs.
#endif


enum Reporting { Silent=0, Verbose=1 };

int factorial(int n) {
	int f = 1;
	while( n>1 ) f*=n--;
	return f;
}

struct Node {
	CharName id;
	bool selected;
	Node *prev, *next;
	Node() : id(-1), selected(false), prev(0), next(0) {}
};

typedef set<int> Meeting;
typedef vector<Meeting> Meetings;

struct Interaction {
	string name;
	CharName id;
	int start, end;
	set<int> members;
	int location;
};

struct Change {
	int time;
	set<int> in, out;
};

vector<int> vectorFromLehmer( size_t k, int n ) {
	int ind, m=k;  
	vector<int> permuted(n);  
	vector<int> elems(n);  
	for(int i=0;i<n;++i) elems[i]=i;  
	for(int i=0;i<n;++i) {  
		ind = m % (n-i);  
		m =  m / (n-i);  
		permuted[i] = elems[ind];  
		elems[ind] = elems[n-i-1];  
	}
	return permuted;
}

struct Perm {
	Node *node;
	int *pos, *elems, *perm;
	int n;
	int count;
	int target;

	bool check( const Meeting &meeting ) {
		count = 0;
		target = static_cast<int>( 2*meeting.size() - 2 ); // target is small
		for( int i=0; i<n; i++ ) node[i].selected = false;
		for( int id : meeting ) {
			node[id].selected = true;
		}
		for( int id : meeting ) {
			if( node[id].prev && node[id].prev->selected == true ) ++count;
			if( node[id].next && node[id].next->selected == true ) ++count;
		}
		return count == target;
	}

	void sub( Node *n ) {
		if( n && n->prev && n->prev->selected ) --count;
		if( n && n->next && n->next->selected ) --count;
	}
	void add( Node *n ) {
		if( n && n->prev && n->prev->selected ) ++count;
		if( n && n->next && n->next->selected ) ++count;
	}


	bool moveAndCheckAgain( Node *w, Node *e, Node *t ) {
		// it might be possible to win constant factors by subbing and adding more carefully...
		Node *q, *r, *y;
		q = w->prev; // could be null
		r = e->next;
		y = t->next; // could be null
		sub(q);
		sub(w);
		sub(e);
		sub(r);
		sub(t);
		sub(y);
		if( q ) q->next = r;
		r->prev = q;
		t->next = w;
		w->prev = t;
		e->next = y;
		if( y ) y->prev = e;
		add(q);
		add(w);
		add(e);
		add(r);
		add(t);
		add(y);
		return count == target;
	}

	bool moveAndCheckAgain( int a, int b, int c ) {
		return moveAndCheckAgain( node+a, node+b, node+c );
	}

	size_t index() {
		// map this permutation to a Lehmer code in [0..n!-1]
		size_t k=0, m=1;
		for( int i=0; i<n; i++ ) {
			pos[i] = i;
			elems[i] = i;
		}
		Node *p = findFirstNode();
		for( int i=0; i<n; ++i ) {
			perm[i] = p->id;
			p = p->next;
		}
		for( int i=0; i<n-1; ++i ) {  
			k += m * pos[perm[i]];  
			m = m * (n-i);  
			pos[elems[n-i-1]] = pos[perm[i]];  
			elems[pos[perm[i]]] = elems[n-i-1];  
		}
		return k;
	}

	Node *findFirstNode() {
		Node *p = node;
		while( p->prev ) {
			p = p->prev;
		}
		return p;
	}

	void list() {
		// print the represented permutation as a list
		Node *p = findFirstNode();
		while( p ) {
			cout << int(p->id) << " ";
			p = p->next;
		}
		cout << endl;
	}

	void list2() {
		// print the internal representation as prev and next pointers
		for( int i=0; i<n; ++i ) {
			cout << i << ":\t" << (node[i].prev?node[i].prev->id:-1) << "\t" << (node[i].next?node[i].next->id:-1) << endl;
		}
		cout << endl;
	}

	Perm( int n ) : count(0), target(0), n(n) {
		node = new Node[n];
		for( int i=0; i<n; ++i ) {
			node[i].id = i;
			if( i>0 ) node[i].prev = node+i-1;
			if( i<n-1 ) node[i].next = node+i+1;
		}
		pos = new int[n];
		elems = new int[n];
		perm = new int[n];
	}
	Perm( vector<int> start ) : count(0),
								target(0),
								n(static_cast<int>(start.size()))  // n is small
								{
		node = new Node[n];
		for( int i=0; i<n; ++i ) {
			node[start[i]].id = start[i];
			if( i>0 ) node[start[i]].prev = node+start[i-1];
			if( i<n-1 ) node[start[i]].next = node+start[i+1];
		}
		pos = new int[n];
		elems = new int[n];
		perm = new int[n];
	}
	~Perm() {
		delete[] node;
		delete[] pos;
		delete[] perm;
		delete[] elems;
	}
};

int parseIntoMeetings( Meetings &meetings, const string &fname ) {
	// This is a terrible mess of a parser, but it should mostly work.
	// There are no sanity checks, so be sure to check once in a while
	// what comes out of it.

	// read file into vector of interactions
	ifstream in(fname);
	vector<Interaction> inters;
	Interaction inter;
	int maxId = -1;
	bool first = true;
	while(in) {
		string token;
		in >> token;
		if( token=="Name" ) {
			// don't push first time.
			if( first ) first = false; else inters.push_back(inter);
			inter = Interaction();
			in >> token;
			in >> inter.name;
			continue;
		}
		if( token=="Id" ) {
			in >> token; in >> inter.id;
			continue;
		}
		if( token=="Start" ) {
			in >> token; in >> inter.start;
			continue;
		}
		if( token=="End" ) {
			in >> token; in >> inter.end;
			continue;
		}
		if( token=="Location" ) {
			in >> token; in >> inter.location;
			continue;
		}
		if( token=="Members" ) {
			in >> token;
			while(true) {
				in >> token;
				if( token[0]=='[' ) token[0]=' ';		
				int memberId = stoi(token);
				if( memberId > maxId ) maxId = memberId;
				inter.members.insert( memberId );
				if( token[token.size()-1]==']' ) break;
			}
		}
	}
	inters.push_back(inter);

	// convert into ordered sequence of changes
	vector<Change> changes;
	for( Interaction &i : inters ) {
		Change c;
		c.time = i.start;
		c.in = i.members;
		changes.push_back(c);
		Change c2;
		c2.time = i.end;
		c2.out = i.members;
		changes.push_back(c2);
	}
	sort( changes.begin(), changes.end(), []( const Change &a, const Change &b ) {
		return a.time < b.time;
	});

	// convert into sequence of meetings
	Meeting m;
	for( Change &c : changes ) {
		for( int i : c.out ) {
			m.erase(i);
			//m.reset(i);
		}
		if( !c.in.empty() ) {
			//for( int i : c.in ) m.set( i );
			for( int i : c.in ) m.insert(i);
			meetings.push_back( m );
		}
	}

	return maxId+1;
}

bool search( Perm &p, const Meetings &meetings, int progress, int limit ) {

	//bool didSomething = false;
	while( p.check(meetings[progress]) ) {
		++progress;
		//didSomething = true;
		if( progress==meetings.size() ) return true;
	}

	//if( !didSomething ) return false;
	if( limit==0 ) return false;

	for( Node *a=p.findFirstNode(); a!=0; a=a->next ) {
		for( Node *b=a; b!=0; b=b->next ) {
			for( Node *c=b->next; c!=0; c=c->next ) {
				{
					// do move
					Node *b2 = b->next;
					p.moveAndCheckAgain(a,b,c);
					// recurse
					if( search( p, meetings, progress, limit-1 ) ) {
						//p.list();
						// undo move
						p.moveAndCheckAgain(b2,c,b);	
						return true;
					}
					// undo move
					p.moveAndCheckAgain(b2,c,b);
				}
				/*{
					// do move with one fewer progress
					Node *b2 = b->next;
					p.moveAndCheckAgain(a,b,c);
					// recurse
					if( progress>0 && search( p, meetings, progress-1, limit-1 ) ) {
						//p.list();
						// undo move
						p.moveAndCheckAgain(b2,c,b);	
						return true;
					}
					// undo move
					p.moveAndCheckAgain(b2,c,b);
				}*/
			}
		}
	}
	return false;
}

template< Reporting Verbose >
int iterativeDeepening( int k, const Meetings &meetings ) {
	if( Verbose ) cout << "[Iterative deepening search.]" << endl;
	int depth = 0;
	while( true ) {
		if( Verbose ) cout << "Searching to depth " << depth << endl;
		bool found = false;
		vector<int> start(k);
		for( int i=0; i<k; ++i ) {
			start[i] = i;
		}
		do {
			Perm p(start);
			if( !p.check(meetings[0]) ) continue;
			if( search( p, meetings, 1, depth) ) {
				//p.list();
				if( Verbose ) cout << "FOUND!" << endl;
				found = true;
				break;
			}
		} while( next_permutation(start.begin(), start.end()) );
		if( found ) break;
		++depth;
	}
	return depth;
}

struct State {
	size_t p;
	int l;
	State( size_t p, int l ) : p(p), l(l) {}
};
template< Reporting Verbose >
int dp( int k, const Meetings &meetings ) {
	if( k>12 ) {
		if( Verbose ) cout << "DP supports at most 12 characters. You lose :(" << endl;
		return -42;
	}
	if( Verbose ) cout << "[Dynamic programming.]" << endl;
	int m = static_cast<int>( meetings.size() );
	int kfac = factorial(k);
	size_t N = kfac * m;

	// ================= JUMP TABLE
	if( Verbose ) cout << "Making jump table ...";
	vector<int> jump(N);
	vector<int> start(k);
	for( int i=0; i<k; ++i ) {
		start[i] = i;
	}
	do {
		Perm p(start);
		size_t pIdx = p.index();
		vector<bool> valid(m,false);
		for( int i=0; i<m; ++i ) {
			valid[i] = p.check(meetings[i]);
		}
		int target = m;
		for( int i=m-1; i>=0; --i ) {
			if( !valid[i] ) target = i;
			jump[pIdx*m + i] = target;
		}
	} while( next_permutation(start.begin(), start.end()) );
	if( Verbose ) cout << "done." << endl;

	// ================ MOVE GRAPH
	if( Verbose ) cout << "Making move graph ... ";
	vector<vector<size_t> > moves(kfac);
	for( int i=0; i<k; ++i ) {
		start[i] = i;
	}
	do {
		Perm p(start);
		size_t pIdx = p.index();
		moves[pIdx].reserve( k*k*k / 6 );
		for( Node *a=p.findFirstNode(); a!=0; a=a->next ) {
			for( Node *b=a; b!=0; b=b->next ) {
				for( Node *c=b->next; c!=0; c=c->next ) {
					// do move
					Node *b2 = b->next;
					p.moveAndCheckAgain(a,b,c);
					// note result
					moves[pIdx].push_back( p.index() );
					// undo move
					p.moveAndCheckAgain(b2,c,b);
				}
			}
		}
	} while( next_permutation(start.begin(), start.end()) );
	if( Verbose ) cout << "done." << endl;

	// ============= DYNAMIC PROGRAMMING
	if( Verbose ) cout << "Dynamic programming ... ";
	vector<int> dp(N);
	vector<size_t> backP(N);
	vector<int> backL(N);
	for( int i=0; i<N; ++i ) {
		// set all dp values to 'unseen'
		dp[i] = numeric_limits<int>::max();
		// initialize all back tracing values to something invalid
		backP[i] = numeric_limits<size_t>::max();
		backL[i] = -1;
	}
	queue<State> Q;
	for( int p=0; p<kfac; ++p ) {
		// set all permutations with l=0 to distance 0
		dp[p*m] = 0;
		// add them to queue
		Q.push( State(p,0) );
	}

	while( !Q.empty() ) {
		State s = Q.front();
		Q.pop();
		for( size_t newP : moves[s.p] ) {
			int newL = jump[newP*m + s.l];
			if( newL == m ) {
				int sol = dp[s.p*m + s.l];
				if( Verbose ) cout << "FOUND at distance " << (sol) << endl;
				cout << "Trace back..." << endl;
				vector<size_t> trace;
				trace.push_back(newP);
				cout << "*** trace L P " << m << " " << newP << endl;
				size_t traceP = s.p;
				int traceL = s.l;
				while( traceL>0 ) {
					cout << "*** trace L P " << traceL << " " << traceP << endl;
					trace.push_back(traceP);
					size_t newP = backP[traceP*m + traceL];
					int newL = backL[traceP*m + traceL];
					traceP = newP;
					traceL = newL;
				}
				reverse(trace.begin(),trace.end());
				for( size_t p : trace ) {
					Perm(vectorFromLehmer(p,k)).list();
				}
				cout << "Trace done." << endl;
				return sol;
			}
			int oldValue = dp[newP*m + newL];
			int newValue = dp[s.p*m + s.l] + 1;
			if( newValue < oldValue ) {
				dp[newP*m + newL] = newValue;
				backP[newP*m + newL] = s.p;
				backL[newP*m + newL] = s.l;
				Q.push( State(newP,newL) );
			}
		}
	}
	if( Verbose ) cout << "\nImpossibru?" << endl;
	return -42;
}

int run_FromFile( int argc, char *argv[] ) {
	// read instance
	Meetings meetings;
	if( argc!=2 ) {
		cout << "need 1 argument: filename" << endl;
		return -1;
	}
	string fname = argv[1];
	int k = parseIntoMeetings( meetings, fname );
	cout << "Instance:" << endl;
	for( Meeting &meet : meetings ) {
		for( int i : meet ) cout << i << " ";
		cout << endl;
	}
	cout << "\n\n";

	// run
	Timer timer;
	int opt = dp<Silent>( k, meetings );
	//int opt = iterativeDeepening( k, meetings );
	cout << "OPT = " << opt << endl;
	timer.report();

	return 0;
}

void writePCSV(string fname, int k, const Meetings &meetings) {
	fname += ".pcsv";
	cout << fname << endl;
	vector<bool> used(k);
	ofstream out(fname);
	int numMeetings = 0;
	for (int i = 0; i < meetings.size(); ++i) {
		numMeetings += 1 + static_cast<int>(k - meetings[i].size());
	}
	out << k << "," << numMeetings << "\n";
	for (int c = 0; c < k; ++c) {
		out << "b,,0,," << c << "\n";
	}
	for (int c = 0; c < k; ++c) {
		out << "d,," << meetings.size() << ",," << c << "\n";
	}
	for (int i = 0; i < meetings.size(); ++i) {
		Meeting m = meetings[i];
		for (int c = 0; c < k; ++c) used[c] = false;
		out << "m,," << i << ",," << (i + 1) << ",,";
		bool first = true;
		for (int c : m) {
			if (!first) out << ",";
			first = false;
			used[c] = true;
			out << c;
		}
		out << "\n";
		for (int c = 0; c < k; ++c) {
			if (!used[c]) {
				out << "m,," << i << ",," << (i + 1) << ",," << c << "\n";
			}
		}
	}
}

void random_uniform( Meetings &meetings, int k, int m, double probInMeeting ) {
	// 'meetings' out argument: the constructed instance
	// k: number of characters
	// m: number of meetings
	// probInmeeting: 'p' from the paper
	for (int i = 0; i<m; ++i) {
		Meeting meet;
		while (meet.size() < 2) {
			meet.clear();
			for (int c = 0; c<k; ++c) {
				if (double(rand()) / RAND_MAX < probInMeeting) {
					meet.insert(c);
				}
			}
		}
		meetings.push_back(meet);
	}
}


random_device rd;
mt19937 rng(rd());
int random(int a, int b) {
	return uniform_int_distribution<int>(a, b - 1)(rng);
}

void random_small(Meetings &meetings, int k, int m, double probInMeeting, int beta) {
	// 'meetings' out argument: the constructed instance
	// k: number of characters
	// m: number of meetings
	// probInmeeting: 'p' from the paper
	// beta: upperbound on the opt number of block crossings in the optimum.
	//       'beta' in the paper.
	vector<vector<int>> perms;
	perms.resize(beta + 1);
	perms[0].resize(k);
	for (int i = 0; i<k; ++i) {
		perms[0][i] = i;
	}
	for (int t = 0; t < beta; ++t) {
		perms[t+1].resize(k);
		vector<int> cut;
		cut.push_back(0);
		cut.push_back(0);
		cut.push_back(0);
		while (cut[1] == cut[2]) {
			cut[0] = random(0, k-1);
			cut[1] = random(0, k-1);
			cut[2] = random(0, k);
			sort(cut.begin(), cut.end());
		}
		int progress = 0;
		for (int i = 0; i < cut[0]; ++i) {
			perms[t + 1][progress++] = perms[t][i];
		}
		for (int i = cut[1] + 1; i <= cut[2]; ++i) {
			perms[t + 1][progress++] = perms[t][i];
		}
		for (int i = cut[0]; i <= cut[1]; ++i) {
			perms[t + 1][progress++] = perms[t][i];
		}
		for (int i = cut[2]+1; i < k; ++i) {
			perms[t + 1][progress++] = perms[t][i];
		}
	}
	vector<Meetings> timeMeetings;
	timeMeetings.resize(beta+1);
	for (int i = 0; i<m; ++i) {
		int t = random(0, beta + 1);
		int size = 0;
		while (size < 2 || size==k) {
			size = 0;
			for (int c = 0; c < k; ++c) {
				if (double(rand()) / RAND_MAX < probInMeeting) ++size;
			}
		}
		Meeting meet;
		int start = random(0, k - size);
		for (int c = start; c < start + size; ++c) {
			meet.insert(perms[t][c]);
		}
		timeMeetings[t].push_back(meet);
	}

	for (int t = 0; t <= beta; ++t) {
		meetings.insert(meetings.end(), timeMeetings[t].begin(), timeMeetings[t].end());
	}

}

int run_RandomInstances( int argc, char *argv[] ) {
	ofstream report( "report.txt" );
	int k = 5;
	int mStart = 20;
	int mEnd = 200;
	int mStep = 20;
	double probInMeeting = 0.5;
	for( int m=mStart; m<=mEnd; m+=mStep ) {
		int runs=10;
		double t = 0;
		for( int run=0; run<runs; ++run ) {
			Meetings meetings;
			//random_small(meetings, k, m, probInMeeting, 5);
			random_uniform(meetings, k, m, probInMeeting);
			string fname = "inst\\instance";
			fname += to_string(k);
			fname += "_m"; fname += to_string(m);
			fname += "_run"; fname += to_string(run);
			writePCSV(fname, k, meetings);
			Timer timer;
			int opt = dp<Silent>( k, meetings );
			//int opt = iterativeDeepening<Silent>(k, meetings);
			t += timer.elapsed();
			cout << k << "\t" << m << "\t" << t << endl;
			report << k << "\t" << m << "\t" << t << endl;
		}
		cout << k << "\t" << m << "\t" << (t / double(runs)) << endl;
		report << k << "\t" << m << "\t" << (t/double(runs)) << endl;
	}
	return 0;
}

void addMeeting(Meetings &meetings, int i, int j) {
	Meeting m;
	m.insert(i-1);
	m.insert(j-1);
	meetings.push_back(m);
}

void printVec(vector<int> v ) {
	for( auto i : v ) cout << i << " ";
	cout << endl;
}

int main( int argc, char *argv[] ) {

	// Test permutation codes both ways
	/*
	int n = 5;
	for( int i=0; i<factorial(n); ++i ) {
		auto vec = vectorFromLehmer( i, n );
		cout << i << endl;
		printVec(vec);
		Perm perm(vec);
		perm.list();
		cout << perm.index() << endl << endl;
	}
	//*/
	
	return run_FromFile(argc,argv);
	//return run_RandomInstances(argc,argv);

}