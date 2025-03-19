import apis_test.get_health_test
import apis_test.post_provider_test
import apis_test.put_provider_test
import apis_test.post_truck_test
import apis_test.put_truck_test
import apis_test.get_truck_test
import apis_test.post_rates_test
import apis_test.get_rates_test
import apis_test.get_bill_test

if __name__ == "__main__":
    # api test

    print('get health check')
    apis_test.get_health_test.run_health_check()


#    print('post provider check')
#    apis_test.post_provider_test.run_post_provider_check()
#
#
#    print('put provider check')
#    apis_test.put_provider_test.run_put_provider_check()
#
#
#    print('post truck check')
#    apis_test.post_truck_test.run_post_truck_check()
#
#
#    print('put truck check')
#    apis_test.put_truck_test.run_put_truck_check()


#    print('get truck check')
#    apis_test.get_truck_test.run_get_truck_check()


    print('post rates check')
    apis_test.post_rates_test.run_post_rates_check()
#
#
#    print('get rates check')
#    apis_test.get_rates_test.run_get_rates_check()
#
#
#    print('get bill check')
#    apis_test.get_bill_test.run_get_bill_check()